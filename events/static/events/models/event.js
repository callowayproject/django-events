var app = app || {};

app.Event = Backbone.Model.extend({
    defaults: {
        start: function(){ return new Date(); },
        end: function(){ var d = new Date(); return d.setHours(d.getHours() + 1); },
        title: "New Event"
    }
});
