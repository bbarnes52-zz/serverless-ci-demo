const octokit = require('@octokit/rest')()
// TODO(bgb): Should we authenticate on every request?
// TODO(bgb): How should we store/token. Token is valid for all github repos for given user. Would oauth make more sense.
octokit.authenticate({
  type: 'token',
  token: '3725add35a99a347576a42df7b42f6bf7ba61151'
});

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
    owner: 'bbarnes52',
    repo: 'ice-cream-sales',
    sha: build.sourceProvenance.resolvedRepoSource.commitSha,
    state: build.status.toLowerCase()
  });
};

// eventToBuild transforms pubsub event message to a build object.
const eventToBuild = (data) => {
  return JSON.parse(new Buffer(data, 'base64').toString());
}

/*
// createSlackMessage create a message from a build object.
const createSlackMessage = (build) => {
  let message = {
   text: `Build \`${build.id}\``,
    mrkdwn: true,
    attachments: [
      {
        title: 'Build logs',
        title_link: build.logUrl,
        fields: [{
          title: 'Status',
          value: build.status
        }]
      }
    ]
  };
  return message
}
*/
