# Models

class Commit extends Spine.Model
    @configure "Commit", "author_avatar", "author_name", "author_email", "message", "time", "repo_name"
    # @belongsTo "repo", "Repo"
    @extend Spine.Model.Ajax
    formattedTime: =>
        moment.utc(@time * 1000).calendar()

class RevfeedCommit extends Commit
    @extend
        url: "/api/revfeed"
        fromJSON: (objects) ->
            return unless objects
            @nextURL = objects.next_url
            new RevfeedCommit(commit) for commit in objects.commits


# Controllers

class Revfeed extends Spine.Controller
    elements:
        ".commits": "$commits"
        ".more": "$more"
    events:
        "click .more a": "more"
    constructor: ->
        super
        RevfeedCommit.bind("refresh", @addAll)
        RevfeedCommit.bind("create", @addOne)
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
            [r, g, b] = ((Math.floor((c % 256) * 0.5) + 128) for c in [r, g, b])
            color = @labelColors[repoName] = r: r, g: g, b: b
        color
    addOne: (commit) =>
        commitItem = new CommitItem(item: commit)
        $commit = commitItem.render().el
        labelColor = @getLabelColor(commit.repo_name)
        $(".repo-name", $commit).css(
            "background-color",
            "rgb(#{labelColor.r}, #{labelColor.g}, #{labelColor.b})"
            )
        @$commits.append($commit)
        return
    addAll: =>
        @$commits.empty()
        RevfeedCommit.each(@addOne)
        return
    more: (e) =>
        e.preventDefault()
        RevfeedCommit.fetch(
            url: RevfeedCommit.nextURL
            success: @proxy (objects) ->
                unless objects.next_url
                    @$more.hide()
            )
        return

class CommitItem extends Spine.Controller
    tag: "li"
    className: "commit"
    render: =>
        @html(Templates.commit(@item))
        @


Templates = {}


$ ->
    Mustache.tags = ["<%", "%>"]
    Templates.commit = Mustache.compile($("#commit-template").remove().html())
    new Revfeed(el: $("#revfeed"))