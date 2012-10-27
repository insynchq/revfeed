# Models

class Commit extends Spine.Model
    @configure "Commit", "author_avatar", "author_name", "author_email", "message", "time"
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
    addOne: (commit) =>
        commit = new CommitItem(item: commit)
        @$commits.append(commit.render().el)
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