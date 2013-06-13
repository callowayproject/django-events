var app = app || {};

app.AppView = Backbone.View.extend({
    el: '#calendar_container',
    initialize: function() {
        _.bindAll(this);
        this.DatePicker = new app.DatePickerWidget({el: $("#datepicker")});
        this.CalendarWidget = new app.FullCalendarWidget({el: $("#calendar")});
        this.CalendarsView = new app.CalendarListView({el: $("#calendarlist"), collection: app.Calendars});
        this.listenTo(app.Calendars, 'change', this.calendarChanged);
        this.DatePicker.render();
        this.CalendarWidget.render({
            viewDisplay: this.calendarViewChanged,
            eventClick: this.eventClick,
            eventResize: this.eventResizeOrDrop,
            eventDrop: this.eventResizeOrDrop
        });
        this.EventSources = {}; // locally cached event sources keyed by slug

    },
    calendarViewChanged: function(view) {
        var _this = this;

        // Remove all the event sources from the calendar widget
        _.each(this.EventSources,
            function(value, key, list){_this.removeEventSource(key);});

        // Cache the current viewable dates
        this.visibleStart = view.visStart;
        this.visibleEnd = view.visEnd;

        // Have all the event sources reload based on visible dates
        this.CalendarsView.collection.each(
            function(item) {
                _this.listenToOnce(item, 'eventsLoaded', _this.addEventSource);
                item.loadEvents(view.visStart, view.visEnd);});
    },
    editEventCallback: function(win, event_id, calendar_slug) {
        win.close();
        this.reloadEventSource(calendar_slug);
    },
    formatDate: function(date) {
        var year = "" + date.getUTCFullYear(),
            month = "00" + date.getUTCMonth(),
            day = "00" + date.getUTCDate(),
            hours = "00" + date.getUTCHours(),
            min = "00" + date.getUTCMinutes();

        var output = year + "-" + month.slice(month.length - 2) + "-" + day.slice(day.length - 2);
        output += " " + hours.slice(hours.length - 2) + ":" + min.slice(min.length - 2);
        return output;
    },
    eventClick: function(event, jsEvent, view) {
        var eventview = new app.EventView({model: new app.Event(event)});
        $(jsEvent.currentTarget).tooltipster({
            content: eventview.render().el.outerHTML,
            position: 'left',
            trigger: 'click',
            theme: event.source.className[0],
            interactive: true
        });
        $(jsEvent.currentTarget).tooltipster('show');
        // if (event.edit_url) {
        //     if (event.edit_url.search(/\?/) >= 0) {
        //         href = event.edit_url + '&_popup=1';
        //     } else {
        //         href = event.edit_url + '?_popup=1';
        //     }
        //     var win = window.open(href, name, 'height=800,width=800,resizable=yes,scrollbars=yes');
        //     win.focus();
        //     return false;
        // }
    },
    eventResizeOrDrop: function(event) {
        // for handling both eventResize and eventDrop callbacks
        if (event.id !== event.event_id) {

        }

    },
    eventChange: function(event) {
        if (event.id !== event.event_id) {

        }
        var updated_event = {
            csrftoken: app.getCookie('csrftoken'),
            id: event.id,
            start: $.fullCalendar.formatDate(event.start, 'yyyy-MM-dd HH:mm'),
            end: $.fullCalendar.formatDate(event.end, 'yyyy-MM-dd HH:mm'),
            all_day: event.allDay,
            title: event.title,
            rule: event.repeating_id
        };
        $.post(event.update_url, updated_event);
    },
    occurrenceChange: function(event) {
        // a specific occurrence is changing
    },
    reloadEventSource: function(slug) {
        // Cause the event source to re-fetch the events. Need to remove the source
        // and add it back after fetching.
        var _this = this;
        var model = this.CalendarsView.collection.findWhere({slug: slug});
        this.removeEventSource(slug);
        this.listenToOnce(model, 'eventsLoaded', this.addEventSource);
        model.loadEvents(this.visibleStart, this.visibleEnd);
    },
    addEventSource: function(slug, source) {
        // Add the source to the cached sources and then to the calendar widget
        this.EventSources[slug] = source;
        this.CalendarWidget.addSource(source);
    },
    removeEventSource: function(key) {
        // Remove the source from the calendar widget and our cached version
        this.CalendarWidget.removeSource(this.EventSources[key]);
        delete this.EventSources[key];
    },
    calendarChanged: function(model, options) {
        if (model.get('checked')) {
            this.listenToOnce(model, 'eventsLoaded', this.addEventSource);
            model.loadEvents(this.visibleStart, this.visibleEnd);
        } else {
            this.removeEventSource(model.get('slug'));
        }
    }
});
