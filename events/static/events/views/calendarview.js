var app = app || {};

app.CalendarView = Backbone.View.extend({
    tagName: "li",
    template: _.template(
        '<input type="checkbox" class="caltoggle" name="<%- slug %>" id="id_<%- slug %>" <%= checked ? "checked" : "" %>>' +
        '&nbsp;<span style="color:<%- color[1] %>;">\u25fc</span>&nbsp;<label for="id_<%- slug %>"><%- name %></label>'),
    events: {
        'click .caltoggle': 'toggleCalendar'
    },
    toggleCalendar: function() {
        this.model.toggle();
    },
    initialize: function(){
        this.listenTo(this.model, 'change', this.render);
    },
    render: function() {
        this.$el.html(this.template(this.model.toJSON()));
        return this;
    }
});
