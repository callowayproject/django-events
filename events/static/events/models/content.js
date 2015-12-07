var app = app || {};

app.Content = Backbone.Model.extend({
});

app.ContentList = PaginatedCollection.extend({
    model: app.Content
});

app.ContentType = Backbone.Model.extend({
/* Should have fields:
    {"model": "quote",
     "app_label": "quotes",
     "id": 15,
     "name": "quote"}
*/
    initialize: function() {
        var _this = this;
        _.bindAll(this);
        this.contenturl = '/events/ajax/contenttypes/' + this.get('id') + '/content/';
        this.contents = new app.ContentList([], {});
        this.contents.baseUrl = this.contenturl;
    },
    loadContent: function(searchterm, callback) {
        var _this = this,
            data = {q: searchterm};
        this.contents.page = 1;
        this.contents.q = searchterm;
        this.contents.fetch({data: data}).done(
            function () {
                if (typeof callback !== "undefined"){
                    callback(_this.contents);
                }
            }
        );
    }
});

app.ContentTypeList = Backbone.Collection.extend({
    model: app.ContentType,
    url: '/events/ajax/contenttypes/'
});

app.ContentTypes = new app.ContentTypeList();