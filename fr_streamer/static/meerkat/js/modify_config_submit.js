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

        if ($('#jsonCheck')[0].checked) {
            d['output']['json'] = {
                'node_frames': parseInt($('#jsonNode').val(), 10),
                'dir': $('#jsonSaveDir').val()
            };
        }
        if ($('#postHttpCheck')[0].checked) {
            d['output']['http_post'] = {
                'url': $('#httpUrl').val(),
                'post_image': $('#http-send-image')[0].checked
            };
        }

        return d;
    }

    ModifyConfig.enableLoading = function () {
        $('.loading-overlay').removeClass('hidden');
    }

    ModifyConfig.disableLoading = function () {
        $('.loading-overlay').addClass('hidden');
    }

    ModifyConfig.bindSubmitButton = function () {
        var self = this;

        $('#submit-button').click( function() {
            self.enableLoading();
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
                },
                complete: function() {
                    self.disableLoading();
                }
            });    
        });
    }

    global.ModifyConfig = ModifyConfig;
    global.ModifyConfig.init();

}(window, jQuery));
