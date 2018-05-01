const octokit = require('@octokit/rest')();
const runtimeConfig = require('cloud-functions-runtime-config');

runtimeConfig.getVariable('ice-cream-sales', 'github-token')
  .then((github_token) => {
    // TODO(bgb): Should we authenticate on every request?
    octokit.authenticate({
      type: 'token',
      token: github_token
    });
  })
  .catch((err) => {
    console.log(err);
    return;
  });

module.exports.subscribe = (event, callback) => {
 const build = eventToBuild(event.data.data);
 console.log("Build results" + JSON.stringify(build));

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
