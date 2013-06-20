var app = app || {};
app.ContentTypeView = Backbone.View.extend({
    template: _.template(
        '<option value="">Select a type</option>' +
        '<% _(contenttypes).each(function(ctype) { %>' +
        '<option value="<%= ctype.id %>"><%= ctype.name %></option>' +
        '<% }); %><br/>'
    ),
    initialize: function() {
        _.bindAll(this);
        this.collection.listenTo(this.collection, 'reset', this.render);
        this.$el.on('change', this.populateList);
        this.collection.fetch({reset: true});
        this.currentModel = null;
    },
    render: function() {
        var ctypes = [];
        _(this.collection.models).each(function(item){
            ctypes.push(item.toJSON());
        });
        this.$el.html(this.template({contenttypes: ctypes}));
        $("#filtercontent").searchbox({process: this.filter});
        return this;
    },
    populateList: function(e) {
        var ctypeID = e.target.value;
        this.currentModel = this.collection.get(ctypeID);
        this.currentModel.loadContent("", this.renderContent);
    },
    filter: function(query) {
        console.log(query);
        this.currentModel.loadContent(query, this.renderContent);
    },
    renderContent: function(contents) {
        var tmpl = _.template(
            '<ul><% _(contents).each(function(c) { %>' +
            '<li class="contentitem" data-objectid="<%= c.attributes.id %>" data-contentid="<%= ctype %>">' +
            '<%= c.attributes.quote %></li>' +
            '<% }); %></ul>'
        );
        $("#contentlist").html(tmpl({'contents': contents.models, 'ctype': this.currentModel.get('id')}));
        $(".contentitem").draggable({
            revert: true,      // immediately snap back to original position
            revertDuration: 0
        });
        $("#filtercontent").show();
    }
});