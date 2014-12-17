var app = app || {};
app.EventView = Backbone.View.extend({
    tagName: "div",
    className: "event-container",
    template: _.template(
        '<div class="ev-title"><%= title %></div>' +
        '<div class="ev-date"><%= daterange %></div>' +
        '<p><%= description %></p>' +
        '<% if (repeats) { %>' +
        // '<a class="btn" href="<%= edit_occurrence_url %>" target="_blank">Edit this occurance</a>' +
        '<a class="btn" href="<%= edit_url %>" target="_blank">Edit all occurances</a>' +
        // '<a class="btn deleteOccurrence" href="<%= delete_occurrence_url %>">Delete this occurance</a>' +
        '<a class="btn delete" href="<%= delete_url %>">Delete all occurances</a>' +
        '<% } else { %>' +
        '<a class="btn" href="<%= edit_url %>" target="_blank">Edit this event</a>' +
        '<a class="btn delete" href="">Delete this event</a>' +
        '<% } %>'
    ),
    initialize: function(){
        this.listenTo(this.model, 'change', this.render);
    },
    render: function() {
        this.$el.html(this.template(this.model.toJSON()));
        return this;
    },
    deleteEvent: function(e) {
        var $this = this;
        e.preventDefault();
        $.post(this.model.get('delete_url'), function(data){});
    }
});