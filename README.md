I've got two versions so far:

1. A basic example that uses the sessions `userId` to persist data between sessions (branch [`simple-demo`](https://github.com/cscanlin/ask-auth/tree/simple-demo)).

2. A more fleshed out version that uses OAuth to link the account to a user in a database ([`master`](https://github.com/cscanlin/ask-auth) branch)

The basic example is based on this bit of information buried in the account linking section:

  > Note that account linking is needed when the skill needs to connect with a system that requires authentication. If your custom skill just needs to keep track of a user to save attributes between sessions, you do not need to use account linking. Instead, you can use the `userId` provided in each request to identify the user. The `userId` for a given user is generated when the user enables your skill in the Alexa app. Every subsequent request from that user to your skill contains the same `userId` unless the user disables the skill.

I suspect that 95% of flask-ask users who think they need account linking, probably just need something more like this (most people who need OAuth are doing almost everything custom).

Both versions currently use the [PynamoDB](https://github.com/pynamodb/PynamoDB) wrapper around AWS DynamoDB NoSQL service, but that adds 5mb overhead to the zipfile for uploading to lambda. It wouldn't be too hard to write a small custom wrapper for `flask-ask`, but the bulk of the overhead may be in the `boto3` package (I haven't tested). If that's the case, I'm not sure it would ever make sense to include in `flask-ask` by default, but it could still be provided as an example or a companion library.

Using a NoSQL db is not a requirement either, but it is the suggested way for most of the basic alexa db use cases. It would relatively trivial to migrate to a RDBS and would probably be better for the next part too.

--------------------------------------------------------------------

The second version is still my final goal, and is based off of this example: https://github.com/lepture/example-oauth2-server/blob/master/app.py

The first part of the flow works, but I still haven't managed to successfully link yet.

The first problem is that the request to link access doesn't seem to include the alexa userId. My plan was to use the alexa userId as the primary key (or hash index w/e) for the user, so the user doesn't have to create a separate account, but I don't see how this would be possible. Right now I'm working around this by storing my userId in an environment variable, but this needs to be solved.

The other problem is that the alexa auth flow seems to work differently than the example. I'm struggling to figure out exactly how the example/library works, but the account linking fails when the alexa app tries to hit the `/oauth/token` endpoint and fails to return a token. The `code` that is set in the `redirect_uri` for `Grant` is provided when the request to `/oauth/token` (I have no idea how the library does it, it doesn't explicitly happen in the `authorize_handler`)

So I think I need to refactor the token model so it can be queried with just the `code`, but that seems like it may be a security risk (maybe it's fine though, I don't know).

In any case, I can answer any other questions, but you'll probably have a better time just testing it yourself, and I need to post this comment now or I never will :P
