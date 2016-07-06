(function (global, $) {

    var ModifyConfig = {};

    ModifyConfig.init = function () {
        this.bindSubmitButton();
    }

    ModifyConfig.getData = function () {
        d = {
            'api_key': $('#apiKeyInput').val,
            'ip': $('#ipInput').val,
            'port': parseInt($('#portInput').val, 10),
            'output': {}
        };

        if ($('#jsonCheck').checked) {
            d['output']['json'] = {
                'node_frames': parseInt($('#jsonNode').val, 10),
                'dir': $('#jsonSaveDir').val
            };
        }
        if ($('#postHttpCheck').checked) {
            d['output']['json'] = {
                'node_frames': parseInt($('#jsonNode').val, 10),
                'dir': $('#jsonSaveDir').val
            };
        }
    }

    ModifyConfig.bindSubmitButton = function () {

        $.ajax({
            type: 'post',
            url: 'insertdata.php',
            data: {
                user_name: name,
                user_age: age,
                user_course: course
            },
            success: function (response) {
                $('#success__para').html("You data will be saved");
            }
        });
    }

    global.ModifyConfig = new ModifyConfig();
    global.ModifyConfig.init();

}(window, jQuery));
