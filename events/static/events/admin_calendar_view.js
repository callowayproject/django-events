$(function() {
    $("#datepicker").datepicker({
        firstDay: 1,
        dayNamesMin: ['S', 'M', 'T', 'W', 'T', 'F', 'S'],
        selectWeek:true,
        selectedWeek: $.datepicker.iso8601Week(new Date()),
        onSelect: function(dateText){
            var selectWeek = $(this).datepicker('option', 'selectWeek'),
                d = new Date(dateText),
                selectedWeek;

            selectedWeek = $.datepicker.iso8601Week(new Date(dateText));
            $(this).datepicker('option', 'selectedWeek', selectedWeek);
            $("#calendar").fullCalendar("gotoDate", d);
            $(this).datepicker('refresh');
        },
        beforeShowDay: function(d){
            var selectWeek = $(this).datepicker('option', 'selectWeek'),
                selectedWeek = $(this).datepicker('option', 'selectedWeek');
            if (!selectWeek) { return [true,''];}
            if (selectedWeek === $.datepicker.iso8601Week(d)){
                  return [true,'ui-state-highlight'];
            }
            return [true,''];
        }
    });
});

$(function(){
    var fullCalendarSelect = function(start, end, allDay) {
            var title = prompt('Event Title:');
            if (title) {
               calendar.fullCalendar('renderEvent',
                  {
                     title: title,
                     start: start,
                     end: end,
                     allDay: allDay
                  },
                  true // make the event "stick"
               );
            }
            calendar.fullCalendar('unselect');
         };

    var Calendar = Backbone.Model.extend({
        defaults: {
            checked: true
        },
        toggle: function() {
            this.set('checked', !this.get('checked'));
        }
    });

    var CalendarView = Backbone.View.extend({
        tag: "li",
        initialize: function(){
            _.bindAll(this, 'render', 'toggle');
        },
        render: function() {
            $(this.el).html('<input type="checkbox" name="' +
                $this.model.get('slug') + '" id="id_' +
                $this.model.get('slug') + '" /><label for="id_' +
                $this.model.get('slug') + '">' +
                $this.model.get('name') +'</label>');
            return this;
        }

    });

    var CalendarList = Backbone.Collection.extend({
        model: Calendar,
        url: '/events/calendars/',
        getChecked: function(){
            return this.where({checked:true});
        }
    });

    var CalendarListView = Backbone.View.extend({
        initialize: function() {
            _.bindAll(this, 'render', 'addAll', 'appendItem');
            this.collection.listenTo(this.collection, 'reset', this.addAll);
            this.collection.fetch();
        },
        render: function() {
            var self = this;
            _(this.collection.models).each(function(item){
                self.appendItem(item);
            });
        },
        addAll: function(){
            alert("BINGO");
            this.collection.each(this.AppendItem, this);
            //this.$el.fullCalendar('addEventSource', this.collection.toJSON());
        },
        appendItem: function(item) {
            var calendarView = new CalendarView({
                model: item
            });
            $('ul', this.el).append(calendarView.render().el);
        }
    });

    var Event = Backbone.Model.extend();

    var Events = Backbone.Collection.extend({
        model: Event,
        url: '/events/calendar/example/events/'
    });

    var EventsView = Backbone.View.extend({
        loadEvents: function(view) {
            var data = {
                start: view.visStart.valueOf() / 1000,
                end: view.visEnd.valueOf() / 1000
            };
            this.collection.fetch({reset: true, data: data});
        },
        initialize: function(){
            _.bindAll(this);
            this.collection.bind('reset', this.addAll);
        },
        render: function() {
            this.$el.fullCalendar({
                editable: true,
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay'
                },
                viewDisplay: this.loadEvents,
                ignoreTimezone: false,
                select: this.select,
                selectable: true,
                selectHelper: true
            });
        },
        addAll: function(){
            this.$el.fullCalendar('addEventSource', this.collection.toJSON());
        },
        select: function(startDate, endDate) {
            // new EventView.render();
            alert("BEEP");
        }
    });

    var events = new Events();
    var eventsview = new EventsView({el: $("#calendar"), collection: events}).render();
    var calendarList = new CalendarList();
    var calendarListView = new CalendarListView({
        el: $("#calendarlist"),
        collection: calendarList}).render();
});