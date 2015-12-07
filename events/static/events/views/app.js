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
            droppable: true,
            drop: this.contentDrop,
            viewDisplay: this.calendarViewChanged,
            eventClick: this.eventClick,
            eventResize: this.eventResizeOrDrop,
            eventDrop: this.eventResizeOrDrop
        });
        this.EventSources = {}; // locally cached event sources keyed by slug
        this.ContentTypePicker = new app.ContentTypeView({el: $('#contenttype_chooser'), collection: app.ContentTypes});
        this.ContentTypePicker.render();
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
    contentDrop: function(date, allDay, jsEvent, ui) {
        console.log("contentDrop");
        var objectid = ui.helper.data('objectid');
        var contentid = ui.helper.data('contentid');
        var _this = this;
        var content_event = {
            csrftoken: app.getCookie('csrftoken'),
            object_id: objectid,
            start: $.fullCalendar.formatDate(date, 'yyyy-MM-dd HH:mm'),
            content_type_id: contentid
        };
        var createEvent = function(calendar_id) {
            content_event.calendar_id = calendar_id;
            $.post('/events/ajax/event_from_content/', content_event, function(data){
                _this.reloadEventSource(data.calendar_slug);
            });
        };
        $.get('/events/ajax/contenttypes/' + contentid + '/calendars/', function(data) {
            if (data.length > 1){
                _this.displaySelectCalendar(data, createEvent);
            } else {
                createEvent(data[0].id);
            }
        });
    },
    chooseCalendarTmpl: _.template(
        '<div id="choose_calendar_dialog">' +
        '<form name="choose_calendar" id="choose_calendar" action="#">' +
        '    <% _(calendars).each(function(calendar, index) { %>' +
        '        <p><input type="radio" value="<%= calendar.id %>" name="calendar_option" id="id_<%= calendar.slug %>"<% if (index === 0) { %> checked="checked" <% }; %>>' +
        '        <label for="id_<%= calendar.slug %>"><%= calendar.name %></label></p>' +
        '    <% }); %>' +
        '</form>' +
        '</div>'
    ),
    displaySelectCalendar: function(calendar_list, callback) {
        var tmpl = this.chooseCalendarTmpl({calendars: calendar_list});
        $(tmpl).appendTo('body').dialog({
            modal: true,
            width: 425,
            height: 275,
            buttons: {
                Cancel: function(){
                    $(this).dialog("close");
                },
                OK: function(){
                    var selected = $('#choose_calendar input[type="radio"]:checked');
                    if (selected.length > 0) {
                        callback(selected.val());
                    }
                    $(this).dialog('close');
                }
            }
        });
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
        var content = $(eventview.render().el.outerHTML);
        var target = $(jsEvent.currentTarget);
        target.tooltipster({
            content: content,
            position: 'left',
            trigger: 'click',
            theme: event.source.className[0],
            interactive: true,
            maxWidth: 300
        });
        target.tooltipster('show', function() {
            this.tooltipster('content').find('.btn.delete').on('click', function(e) {
                eventview.deleteEvent(e);
                target.tooltipster('hide');
                target.remove();
            });
        });

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
        if (event.id !== event.event_id) { }
        var startDatetime = $.fullCalendar.formatDate(event.start, 'yyyy-MM-dd HH:mm');
        if (event.end === null && event.allDay) {
            var endDatetime = $.fullCalendar.formatDate(event.start, 'yyyy-MM-dd') + ' 23:59';
        } else {
            var endDatetime = $.fullCalendar.formatDate(event.end, 'yyyy-MM-dd HH:mm');
        }
        var updated_event = {
            csrftoken: app.getCookie('csrftoken'),
            id: event.id,
            start: startDatetime,
            end: endDatetime,
            all_day: event.allDay,
            title: event.title,
            rule: event.repeating_id
        };
        $.post(event.update_url, updated_event);
    },
    eventChange: function(event) {
        if (event.id !== event.event_id) { }
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
