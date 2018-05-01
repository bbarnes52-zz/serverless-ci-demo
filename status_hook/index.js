console.log("Starting cloud function");
const octokit = require('@octokit/rest')();
const Storage = require('@google-cloud/storage');
const projectId = 'pso-data-ml';
const gcs = new Storage({
  projectId: projectId,
});
// TODO(bgb): Handle err.
const file = gcs.bucket('ice-cream-sales-keys').file('github-token.txt.enc');
file.download(function(err, contents) {
  if (err) {
    console.log(err);
    return;
  }
  const request = {
    name: `projects/pso-data-ml/locations/global/keyRings/ice-cream-sales/cryptoKeys/github`,
    resource: {
      ciphertext: contents
    }
  };
  // Decrypts the file using the specified crypto key
  cloudkms.projects.locations.keyRings.cryptoKeys.decrypt(request, (err, response) => {
    if (err) {
      console.log(err);
      return;
    }

    const result = response.data;
    console.log(result.plaintext);
    // TODO(bgb): Should we authenticate on every request?
    octokit.authenticate({
      type: 'token',
      token: result.plaintext
    });
  });
});

console.log("Ending cloud function");

module.exports.subscribe = (event, callback) => {
 const build = eventToBuild(event.data.data);
 console.log("Build results" + JSON.stringify(build));

// Skip if the current status is not in the status list.
// Add additional statues to list if you'd like:
// QUEUED, WORKING, SUCCESS, FAILURE,
// INTERNAL_ERROR, TIMEOUT, CANCELLED
  const status = ['SUCCESS', 'FAILURE', 'INTERNAL_ERROR', 'TIMEOUT'];
  if (status.indexOf(build.status) === -1) {
    return callback();
  }

  octokit.repos.createStatus({
    // TODO(bgb): Add `description` field for GitHub UI.
    owner: 'bbarnes52',
    repo: 'ice-cream-sales',
    sha: build.sourceProvenance.resolvedRepoSource.commitSha,
    state: build.status.toLowerCase(),
    target_url: build.logUrl
  });
};

// eventToBuild transforms pubsub event message to a build object.
const eventToBuild = (data) => {
  return JSON.parse(new Buffer(data, 'base64').toString());
}
