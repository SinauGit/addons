odoo.define('aa_pendaftaran_online.website_online_registration_system', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    $(document).on('click', "#submit_button", function () {

        var name = $("#name").val();
        var phone = $("#phone").val();
        var email = $("#email").val();
        var mobile = $("#mobile").val();
        var street = $("#street").val();
        var jenjang = $("#jenjang").val();

        if (name == "" || mobile == "" || phone == "" || email == "" || street == "" || jenjang == "") {
            alert("Semua kolom bertanda (*) mohon diisi");
        } else {
            var booking_record = {
                'name': name,
                'phone': phone,
                'email': email,
                'mobile': mobile,
                'street': street,
                'jenjang': jenjang
            };
            $.ajax({
                url: "/page/registration_details",
                type: "POST",
                dataType: "json",
                data: booking_record,
                type: 'POST',
                success: function (data) {
                    window.location.href = "/page/aa_pendaftaran_online.akhir_html";
                },
                error: function (error) {
                    alert('error: ' + error);
                }
            });
        }
    });
});