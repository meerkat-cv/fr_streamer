(function (global, $) {

    var ModifyConfig = {};

    ModifyConfig.init = function () {
        this.bindSubmitButton();
    }

    ModifyConfig.showError = function (server_error) {
        if (server_error) {
            $('.alert-danger').children('#server_response').html(server_error);    
        }
        $('.alert-danger').removeClass('hidden');
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
        var self = this;

        $('#submit-button').click( function() {
            $.ajax({
                type: 'post',
                url: '/fr_streamer/config/modify_server',
                data: self.getData(),
                sucess: function (response) {
                    console.log('done!');
                    $('#success__para').html("You data will be saved");
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    self.showError(jqXHR.responseText);
                }
            });    
        });
    }

    global.ModifyConfig = ModifyConfig;

    global.ModifyConfig.init();

}(window, jQuery));
