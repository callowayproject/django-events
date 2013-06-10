var app = app || {};

app.CalendarList = Backbone.Collection.extend({
    model: app.Calendar,
    url: '/events/calendars/',
    getChecked: function(){
        return this.where({checked:true});
    }
});

app.Calendars = new app.CalendarList();