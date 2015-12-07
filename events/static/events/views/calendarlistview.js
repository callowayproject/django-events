var app = app || {};

app.CalendarListView = Backbone.View.extend({
    // [ [border, background], ...]
    colorPalette: [
        ["#75481E", "#AC725E"], ["#924420", "#D06B64"], ["#A64232", "#F83A22"],
        ["#D02424", "#FA573C"], ["#BB5517", "#FF7537"], ["#CB7403", "#FFAD46"],

        ["#50B68E", "#42D692"], ["#06813f", "#20ab6c"], ["#4DB810", "#7BD148"],
        ["#94c110", "#b6dd72"], ["#BDB634", "#FBE983"], ["#c2990d", "#fad26b"],

        ["#38b896", "#96e2c2"], ["#13beb5", "#a2e2e7"], ["#1c8abf", "#a2c8e7"],
        ["#3173d2", "#518be8"], ["#373AD7", "#9A9CFF"], ["#6733DD", "#B99AFF"],

        ["#979797", "#cdcdcd"], ["#717171", "#CABDBF"], ["#8A404D", "#CCA6AC"],
        ["#D21E5B", "#F691B2"], ["#CA2AE6", "#CD74E6"], ["#9C3CE4", "#A47AE2"]
    ],
    initialize: function() {
        _.bindAll(this);
        this.index = 0;
        this.collection.listenTo(this.collection, 'reset', this.addAll);
        this.collection.fetch({reset: true});
    },
    render: function() {
        var self = this;
        _(this.collection.models).each(function(item){
            self.appendItem(item);
        });
    },
    addAll: function(){
        this.collection.each(this.appendItem, this);
    },
    appendItem: function(item) {
        item.set({
            'className': "cal" + this.index,
            'color': this.colorPalette[this.index++]
        });
        var calendarView = new app.CalendarView({
            model: item
        });
        this.$el.append(calendarView.render().el);
    }
});
