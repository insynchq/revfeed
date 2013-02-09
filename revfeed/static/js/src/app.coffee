# Models

class Commit extends Spine.Model
    @configure "Commit", "author_avatar", "author_name", "author_email",
        "message", "time", "repo_name", "new"
    @extend Spine.Model.Ajax
    formattedTime: =>
        moment.utc(@time * 1000).calendar()

class RevfeedCommit extends Commit
    @extend
        url: "api/revfeed"
        fromJSON: (objects) ->
            return unless objects
            @nextURL = objects.next_url
            new RevfeedCommit(commit) for commit in objects.commits


# Controllers

class Revfeed extends Spine.Controller
    elements:
        ".commits": "$commits"
        ".older": "$older"
        ".new-commits": "$newCommits"
    events:
        "click .older a": "olderCommits"
        "click .new-commits a": "showNewCommits"
    newCommits: 0
    constructor: ->
        super
        RevfeedCommit.bind("create", @addCommit)
        RevfeedCommit.bind("refresh", @addCommits)
        RevfeedCommit.fetch()
        return
    getLabelColor: (repoName) ->
        color = @labelColors?[repoName]
        unless color
            [r, g, b] = [0, 0, 0]
            @labelColors = @labelColors or {}
            repoName.split("").map((c, i) ->
                charCode = c.charCodeAt(0)
                unless i % 1
                    r += charCode
                unless i % 3
                    g += charCode
                unless i % 5
                    b += charCode
                )
            [r, g, b] = ((Math.floor((c % 256) * 0.25) + 192) for c in [r, g, b])
            color = @labelColors[repoName] = r: r, g: g, b: b
        color
    addCommit: (commit) =>
        commitItem = new CommitItem(item: commit)
        $commit = commitItem.render().el
        labelColor = @getLabelColor(commit.repo_name)
        $(".repo-name", $commit).css(
            "background-color",
            "rgb(#{labelColor.r}, #{labelColor.g}, #{labelColor.b})"
            )
        if commit.new
            # Update new commits
            @newCommits++
            @$newCommits
                .html(Templates.newCommits(new_commits: @newCommits))
                .show()
            # Prepend new commit
            @$commits.prepend($commit.addClass("new"))
        else
            @$commits.append($commit)
        return
    addCommits: (commits) =>
        commits.forEach(@addCommit)
        return
    olderCommits: (e) =>
        e.preventDefault()
        RevfeedCommit.fetch(
            url: RevfeedCommit.nextURL
            success: @proxy (objects) ->
                unless objects.next_url
                    @$older.hide()
            )
        return
    showNewCommits: (e) =>
        e.preventDefault()
        @newCommits = 0
        @$newCommits.hide()
        @$(".new", @$commits).removeClass("new")


class CommitItem extends Spine.Controller
    tag: "li"
    className: "commit"
    render: =>
        @html(Templates.commit(@item))
        @


# Templates

Templates = {}


$ ->
    Mustache.tags = ["<%", "%>"]
    Templates.commit = Mustache.compile($("#commit-template").remove().html())
    Templates.newCommits = Mustache.compile($("#new-commits-template").remove().html())
    new Revfeed(el: $("#revfeed"))


# Socket.IO

WEB_SOCKET_SWF_LOCATION = "/static/WebSocketMain.swf"

path = location.pathname.replace(/^\/+|\/+$/g, '')
resource = "socket.io"
if path.length
    resource = "#{path}/#{resource}"
notifier = io.connect(
    "/notifier",
    resource: resource
    )

notifier.on("revfeed", (commits) ->
    for commit in commits
        commit.new = true
        RevfeedCommit.create(commit, ajax: false)
    return
    )
