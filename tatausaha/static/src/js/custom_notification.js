odoo.define('surat_masuk.custom_notification', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;

    var CustomNotification = {
        showNotification: function(self) {
            self.do_notify(_t("Sukses"), _t("Data surat masuk berhasil ditambahkan."), true, 'success');
        }
    };

    return {
        showNotification: CustomNotification.showNotification
    };
});