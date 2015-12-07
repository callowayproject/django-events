var app = app || {};

app.FullCalendarWidget = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this);
    },
    render: function(options) {
        this.$el.fullCalendar({
            editable: true,
            droppable: options.droppable || false,
            drop: options.drop || this.drop,
            eventClick: options.eventClick || this.eventClick,
            eventDrop: options.eventDrop || this.eventDrop,
            eventResize: options.eventResize || this.eventResize,
            header: {
                left: 'prev,next today',
                center: 'title',
                right: 'month,agendaWeek,agendaDay'
            },
            viewDisplay: options.viewDisplay,
            ignoreTimezone: true,
            select: options.select || this.select,
            selectable: true,
            selectHelper: true
        });
        return this;
    },
    eventClick: function(event, jsEvent, view) {
        alert("FullCalendarWidget.eventClick:" + event.id);
    },
    eventDrop: function(event, dayDelta, minuteDelta, allDay, revertFunc, jsEvent, ui, view) {
        alert(
            event.title + " was moved " +
            dayDelta + " days and " +
            minuteDelta + " minutes."
        );

        if (allDay) {
            alert("Event is now all-day");
        }else{
            alert("Event has a time-of-day");
        }
    },
    eventResize: function(event, dayDelta, minuteDelta, revertFunc, jsEvent, ui, view) {
        alert("FullCalendarWidget.eventResize: moved:"+dayDelta+" days, "+minuteDelta+"minutes");
    },
    drop: function(date, allDay) {
        alert("Dropped on " + date + " with allDay=" + allDay);
    },
    select: function(startDate, endDate) {
        alert("FullCalendarWidget.select: "+startDate+" - "+endDate);
    },
    addSource: function(source){
        this.$el.fullCalendar('addEventSource', source);
    },
    removeSource: function(source){
        this.$el.fullCalendar('removeEventSource', source);
    },
    renderEvent: function(event, stick) {
        this.$el.fullCalendar('renderEvent', event, stick);
    }
});