var app = app || {};

app.DatePickerWidget = Backbone.View.extend({
    render: function() {
        this.$el.datepicker({
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
    }
});