import os

import aiohttp

from aiohttp import web

from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()

@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    """ Whenever an issue is opened, greet the author and say thanks."""
    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]
    message = f"Thanks for the report @{author}! I will look into it ASAP! (I'm a bot)."

    await gh.post(url, data={"body": message})
    pass

@router.register("pull_request", action="closed")
async def pull_request_merged(event, gh, *args, **kwargs):
    """ Whenever a pull request is merged, say thanks """
    url = event.data["pull_request"]["comments_url"]
    author = event.data["pull_request"]["user"]["login"]
    is_merged = event.data["pull_request"]["merged"]
    
    if is_merged:
        message = f"thanks for the PR @{user}"
        await gh.post(url, data={"body":message})

@router.register("issue_comment", action="created")
async def issue_comment_created_event(event, gh, *args, **kwargs):
    """thumbs up my own comments"""
    url=f"{event.data['comment']['url']}/reactions"
    user = event.data["comment"]["user"]["login"]
    if user == "mbgrad":
        await gh.post(url,
                      data={'content':'+1'},
                      accept="application/vnd.github.squirrel-girl-preview+json"
                      )

async def main(request):
    
    # read the GitHub webhook payload
    body = await request.read()

    # our authentication token and secret
    secret = os.environ.get("GH_SECRET")
    oauth_token = os.environ.get("GH_AUTH")

    # a representation of GitHub webhook event
    event = sansio.Event.from_http(request.headers, body, secret=secret)

    # instead of mariatta, use your own username
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "mbgrad",
                                  oauth_token=oauth_token)

        # call the appropriate callback for the event
        await router.dispatch(event, gh)

    # return a "Success"
    return web.Response(status=200)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)

    web.run_app(app, port=port)