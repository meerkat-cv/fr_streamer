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

    ModifyConfig.showSuccess = function () {
        $('.alert-success').removeClass('hidden');
    }

    ModifyConfig.getData = function () {
        var d = {
            'api_key': $('#apiKeyInput').val(),
            'ip': $('#ipInput').val(),
            'port': parseInt($('#portInput').val(), 10),
            'output': {}
        };

        if ($('#jsonCheck').checked) {
            d['output']['json'] = {
                'node_frames': parseInt($('#jsonNode').val(), 10),
                'dir': $('#jsonSaveDir').val()
            };
        }
        if ($('#postHttpCheck').checked) {
            d['output']['http_post'] = {
                'node_frames': parseInt($('#jsonNode').val(), 10),
                'dir': $('#jsonSaveDir').val
            };
        }

        return d;
    }

    ModifyConfig.bindSubmitButton = function () {
        var self = this;

        $('#submit-button').click( function() {
            $.ajax({
                type: 'post',
                url: '/fr_streamer/config/modify_server',
                data: JSON.stringify(self.getData()),
                contentType: 'application/json',
                success: function (response) {
                    self.showSuccess();
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
