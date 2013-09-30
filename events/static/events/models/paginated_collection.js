// from https://gist.github.com/io41/838460
// includes bindings for fetching/fetched

var PaginatedCollection = Backbone.Collection.extend({
  initialize: function() {
    _.bindAll(this, 'parse', 'url', 'pageInfo', 'nextPage', 'previousPage');
    this.page = 1;
    if (typeof this.perPage === 'undefined') { this.perPage = 5; }
  },
  fetch: function(options) {
    options = options || {};
    this.trigger("fetching");
    var self = this;
    var success = options.success;
    options.success = function(resp) {
      self.trigger("fetched");
      if(success) { success(self, resp); }
    };
    return Backbone.Collection.prototype.fetch.call(this, options);
  },
  parse: function(resp) {
    this.page = resp.page;
    this.perPage = resp.perPage;
    this.total = resp.total;
    return resp.models;
  },
  url: function() {
      return this.baseUrl + '?' + $.param({page: this.page, perPage: this.perPage, q:this.q});
  },
  pageInfo: function() {
    var info = {
      total: this.total,
      page: this.page,
      perPage: this.perPage,
      pages: Math.ceil(this.total / this.perPage),
      prev: false,
      next: false
    };

    var max = Math.min(this.total, this.page * this.perPage);

    if (this.total == this.pages * this.perPage) {
      max = this.total;
    }

    info.range = [(this.page - 1) * this.perPage + 1, max];

    if (this.page > 1) {
      info.prev = this.page - 1;
    }

    if (this.page < info.pages) {
      info.next = this.page + 1;
    }

    return info;
  },
  nextPage: function(callback) {
    if (!this.pageInfo().next) {
      return false;
    }
    this.page = this.page + 1;
    var _this = this;
    return this.fetch().done(
        function () {
            if (typeof callback !== "undefined"){
                callback(_this);
            }
        }
    );
  },
  previousPage: function(callback) {
    if (!this.pageInfo().prev) {
      return false;
    }
    this.page = this.page - 1;
    var _this = this;
    return this.fetch().done(
        function () {
            if (typeof callback !== "undefined"){
                callback(_this);
            }
        }
    );
  }

});
