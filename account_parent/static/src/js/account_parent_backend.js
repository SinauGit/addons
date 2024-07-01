odoo.define('account_parent.coa_heirarchy', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var session = require('web.session');
//var Widget = require('web.Widget');
var ControlPanelMixin = require('web.ControlPanelMixin');
var session = require('web.session');
var CoAWidget = require('account_parent.CoAWidget');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var QWeb = core.qweb;

var coa_heirarchy = AbstractAction.extend(ControlPanelMixin, {
    // Stores all the parameters of the action.
    init: function(parent, action) {
        this.actionManager = parent;
        this.given_context = action.context;
        
        this.controller_url = action.context.url;
        if (action.context.context) {
            this.given_context = action.context.context;
        }
        
//        this.given_context.active_id = action.context.active_id || action.params.active_id;
//        this.given_context.model = action.context.active_model || false;
//        this.given_context.ttype = action.context.ttype || false;
        return this._super.apply(this, arguments);
    },
    willStart: function() {
        return this.get_html();
    },
    set_html: function() {
        var self = this;
        var def = $.when();
        if (!this.report_widget) {
            this.report_widget = new CoAWidget(this, this.given_context);
            def = this.report_widget.appendTo(this.$el);
        }
        return def.then(function () {
            self.report_widget.$el.html(self.html);
        });
    },
    start: function() {
    	var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.set_html();
        });
    },
    // Fetches the html and is previous report.context if any, else create it
    get_html: function() {
        var self = this;
        var defs = [];
        return this._rpc({
                model: 'account.open.chart',
                method: 'get_html',
                args: [self.given_context],
            })
            .then(function (result) {
                self.html = result.html;
                self.renderButtons();
                defs.push(self.update_cp());
                return $.when.apply($, defs);
            });
    },
    // Updates the control panel and render the elements that have yet to be rendered
    update_cp: function() {
        if (!this.$buttons) {
            this.renderButtons();
        }
        var status = {
//            breadcrumbs: this.actionManager.get_breadcrumbs(),
            cp_content: {$buttons: this.$buttons},
        };
        return this.update_control_panel(status);
    },
    renderButtons: function() {
        var self = this;
        var parent_self = this;
        this.$buttons = $(QWeb.render("coaReports.buttons", {}));
        this.$buttons.bind('click', function () {
        	if (this.id == "export_treeview_xls"){
        		//xls output
                var self = parent_self,
                    view = parent_self.getParent(),
                    children = view.getChildren();
                var c = crash_manager;
                var $element = $(parent_self.$el[0]).find('.table-responsive tbody tr');
                var dict = [];

                $element.each(function( index ) {
                    var $el = $($element[index]);
                    dict.push({
                            'id': $el.data('id'),
                            'wiz_id': $el.data('wiz_id'),
                            'model_id': $el.data('model_id'),
                            'unfoldable': $el.data('unfold'),
                            'level': $el.find('td:first').data('level') || 1
                    });
                });
                $.blockUI();
                var url_data = parent_self.controller_url.replace('active_id', parent_self.given_context['active_id']);
                url_data = url_data.replace('account_parent', 'account_parent_xls')
                url_data = url_data.replace('output_format', 'xls')
                session.get_file({
                    url: url_data,
                    data: {data: JSON.stringify({
                        model: view.modelName,
                        wiz_id: parent_self.given_context['active_id'],
                        report_data: JSON.stringify(dict), 
                    })},
                    complete: $.unblockUI,
                    error: c.rpc_error.bind(c)
                });
        		
        	}	
        	else{
        		// pdf output
                var $element = $(parent_self.$el[0]).find('.table-responsive tbody tr');
                var dict = [];

                $element.each(function( index ) {
                    var $el = $($element[index]);
                    dict.push({
                            'id': $el.data('id'),
                            'wiz_id': $el.data('wiz_id'),
                            'model_id': $el.data('model_id'),
                            'unfoldable': $el.data('unfold'),
                            'level': $el.find('td:first').data('level') || 1
                    });
                });
                framework.blockUI();
                var url_data = parent_self.controller_url.replace('active_id', parent_self.given_context['active_id']);//self.given_context.active_id
                url_data = url_data.replace('output_format', 'pdf')
                session.get_file({
                    url: url_data,
                    data: {data: JSON.stringify(dict)},
                    complete: framework.unblockUI,
                    error: crash_manager.rpc_error.bind(crash_manager),
                });
        	}
        });
        return this.$buttons;
    },
    do_show: function() {
        this._super();
        this.update_cp();
    },
});

core.action_registry.add("coa_heirarchy", coa_heirarchy);
return coa_heirarchy;
});
