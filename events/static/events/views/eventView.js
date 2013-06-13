var app = app || {};
app.EventView = Backbone.View.extend({
    tagName: "div",
    className: "event-container",
    template: _.template(
        '<div class="ev-title"><%= title %></div>' +
        '<div class="ev-date"><%= daterange %></div>' +
        '<p><%= description %></p>' +
        '<% if (repeats) { %>' +
        '<a class="btn" href="<%= edit_url %>">Edit this occurance</a><br/>' +
        '<a class="btn" href="<%= edit_url %>">Edit all occurances</a>' +
        '<% } else { %>' +
        '<a class="btn" href="<%= edit_url %>">Edit this event</a>' +
        '<% } %>'
    ),
    initialize: function(){
        this.listenTo(this.model, 'change', this.render);
    },
    render: function() {
        this.$el.html(this.template(this.model.toJSON()));
        return this;
    }
});