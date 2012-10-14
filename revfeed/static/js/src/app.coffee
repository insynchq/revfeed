# Models

class Commit extends Spine.Model
    @configure "Commit", "author", "message", "time"
    @belongsTo "repo", "Repo"
    formattedTime: =>
        moment.utc(@time).calendar()

class Repo extends Spine.Model
    @configure "Repo", "name", "path", "commits", "start", "next"
    @hasMany "commits", "Commit"
    @extend Spine.Model.Ajax
    @extend
        url: "/api/repos"
        fromJSON: (objects) ->
            unless objects
                return
            if objects?.repos
                new Repo(repo) for repo in objects.repos
            else
                new Repo(objects)
    constructor: (objects) ->
        super
        @commits().create(commit) for commit in objects.commits


# Controllers

class Revfeed extends Spine.Controller
    constructor: ->
        super
        Repo.bind("create", @addRepo)
        Repo.bind("refresh", @addRepos)
        Repo.fetch()
    addRepo: (repo) =>
        view = new Repos(item: repo)
        @el.append(view.render().el)
    addRepos: =>
        @el.empty() # Remove loading text
        Repo.each(@addRepo)

class Repos extends Spine.Controller
    tag: "div"
    className: "repo"
    events:
        "click .more a": "more"
    elements:
        ".commits": "$commits"
        ".more": "$more"
    render: =>
        @html(Templates.repo(@item))
        @addCommits(@item.commits().all())
        unless @item.next
            @$(".more").hide();
        @
    addCommit: (commit) =>
        view = new Commits(item: commit)
        @$commits.append(view.render().el)
    addCommits: (commits) =>
        commits.map(@addCommit)
    more: (e) =>
        e.preventDefault()
        if @item.next
            @item.ajax().reload
                url: @item.next
                success: @proxy((objects) ->
                    for commit in objects.commits
                        @item.commits().create(commit)
                        @addCommit(@item.commits().last())
                    unless objects.next
                        @$(".more").hide()
                    )
        return

class Commits extends Spine.Controller
    tag: "li"
    className: "commit"
    render: =>
        @html(Templates.commit(@item))
        @


Templates = {}


$ ->
    Mustache.tags = ["<%", "%>"]
    Templates.repo = Mustache.compile($("#repo-template").remove().html())
    Templates.commit = Mustache.compile($("#commit-template").remove().html())
    new Revfeed(el: $("#revfeed"))