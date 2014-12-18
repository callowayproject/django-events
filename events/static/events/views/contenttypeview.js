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
        this.collection.bind('refresh', this.render);
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
    previous: function() {
        this.contents.previousPage(this.renderContent);
        return false;
    },
    next: function() {
        this.contents.nextPage(this.renderContent);
        return false;
    },
    populateList: function(e) {
        var ctypeID = e.target.value;
        this.currentModel = this.collection.get(ctypeID);
        //this.currentModel.loadContent("", this.renderContent);
        $("#filtercontent").show();
        this.filter("");
    },
    filter: function(query) {
        this.currentModel.loadContent(query, this.renderContent);
    },
    renderContent: function(contents) {
        var tmpl = _.template(
            '<ul><% _(contents).each(function(c) { %>' +
            '<li class="contentitem" data-objectid="<%= c.attributes.id %>" data-contentid="<%= ctype %>">' +
            '<%= c.attributes.description %></li>' +
            '<% }); %></ul>'
        );
        var pag_tmpl = _.template(
            '<div class="pagination">' +
            '  <% if (prev) { %><a href="#" id="prev" class="clearfix"><% } %>' +
            '    <span class="ui-icon ui-icon-circle-triangle-w">Prev</span>' +
            '  <% if (prev) { %></a><% } %>' +
            '  Page <%= page %> of <%= pages %>' +
            '  <% if (next) { %><a href="#" id="next" class="clearfix"><% } %>' +
            '    <span class="ui-icon ui-icon-circle-triangle-e">Next</span>' +
            '  <% if (next) { %></a><% } %>' +
            '</div>'
        );
        $("#contentlist").html(tmpl({'contents': contents.models, 'ctype': this.currentModel.get('id')}));
        var pag = pag_tmpl(contents.pageInfo());
        this.contents = contents;
        $("#contentlist").prepend(pag);
        $("#prev").click(this.previous);
        $("#next").click(this.next);
        $(".contentitem").draggable({
            revert: true,      // immediately snap back to original position
            revertDuration: 0
        });
        $('.contentitem').tooltipster({
           content: 'Loading...',
           updateAnimation: false,
           position: 'right',
           contentAsHTML: true,
           functionBefore: function(origin, continueTooltip) {

              // we'll make this function asynchronous and allow the tooltip to
              // go ahead and show the loading notification while fetching our
              // data
              continueTooltip();

              // next, we want to check if our data has already been cached
              if (origin.data('ajax') !== 'cached') {
                 $.ajax({
                    type: 'GET',
                    url: '/events/ajax/contenttypes/' + origin.data('contentid') + '/content/' + origin.data('objectid') + '/',
                    success: function(data) {
                       // update our tooltip content with our returned data and cache it
                       origin.tooltipster('update', data).data('ajax', 'cached');
                    }
                 });
              }
           }
        });

        $("#filtercontent").show();
    }
});