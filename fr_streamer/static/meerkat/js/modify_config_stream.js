(function (global, $) {

    var ModifyConfigStream = {};

    ModifyConfigStream.init = function () {
        var self = this;
        $(document).ready(function () {
            self.bindModalEvents();
            self.bindEditButtons();
            self.bindDeleteButtons();
        });
    }

    ModifyConfigStream.getData = function () {
        var d = {
            'label': $('#streamLabel').val()
        };

        if ($('#radioCamera')[0].checked) {
            d['camera_url'] = $('#cameraVideoUrl').val();
        }
        else if ($('#radioVideo')[0].checked) {
            d['video_file'] = $('#cameraVideoUrl').val();
        }

        d['tempCoherence'] = {};
        if ($('#temporalWin').val() && $('#thresholdInput').val()) {
            d['tempCoherence']['tempWindow'] = parseInt($('#temporalWin').val(),10);
            d['tempCoherence']['threshold'] = parseInt($('#thresholdInput').val(),10);
        }
        return d;
    }

    ModifyConfigStream.bindModalEvents = function () {
        this.bindModalRadioButtons();

        var self = this;
        $('#modal-stream').on('hidden.bs.modal', function () {
            self.clearModalValues();
        });

        $('#saveChangesButton').click(function () {
            // self.enableLoading();
            console.log('save Changes!');
            $.ajax({
                type: 'post',
                url: '/fr_streamer/config/upsert_stream',
                data: JSON.stringify(self.getData()),
                contentType: 'application/json',
                complete: function() {
                    location.reload();
                }
            });
        });
    }

    ModifyConfigStream.bindDeleteButtons = function () {
        var self = this;
        $('#streams-table a.del-stream').click(function (event) {
            var iid = parseInt($(this).attr("id").slice(10), 10),
                trElement = $('#streams-table > tbody > tr').get(iid),
                label = $(trElement).children('td')[0].innerHTML;
            $('#confirm-delete-label').html(label);
            $('#modal-confirm-delete').modal('show');
        });

        $('#confirm-delete-button').click(function() {
            console.log('Delete button')
            var label = $('#confirm-delete-label').html();
            $.ajax({
                type: 'delete',
                url: '/fr_streamer/config/remove_stream/'+label,
                complete: function() {
                    location.reload();
                }
            });
        });
        
    }


    ModifyConfigStream.bindModalRadioButtons = function () {
        $('#radioCamera').on('ifChecked', function (event) {
            $('#cameraVideoUrl').attr('placeholder', 'rtsp://yourcamera/url.mpeg')
            $('#cameraVideoLabel').html('Camera Url (RTP/RTSP/HTTP):')
        });
        $('#radioVideo').on('ifChecked', function (event) {
            $('#cameraVideoUrl').attr('placeholder', '/path/to/your/video.mp4')
            $('#cameraVideoLabel').html('Video file path:')
        });
    }

    ModifyConfigStream.bindEditButtons = function () {
        var self = this;
        $('#streams-table a.edit-stream').click(function (event) {
            var iid = parseInt($(this).attr("id").slice(11), 10);
            self.setModalValues($('#streams-table > tbody > tr').get(iid));
            $('#modal-stream').modal('show');
        });
    }

    ModifyConfigStream.clearModalValues = function () {
        $('#streamLabel').removeAttr('disabled');
        $('#streamLabel').val('');
        $('#radioCamera').iCheck('check');
        $('#cameraVideoUrl').val('')
        $('#temporalWin').val('');
        $('#thresholdInput').val('');
    }


    ModifyConfigStream.setModalValues = function (trElement) {
        if (trElement) {
            var values = $(trElement).children('td');
            
            var label = values[0].innerHTML,
                type = values[1].innerHTML,
                path = values[2].innerHTML,
                threshold = values[3].innerHTML,
                temporal_win = values[4].innerHTML;

            $('#streamLabel').val(label);
            $('#streamLabel').attr('disabled','disabled');
            if (type === 'Camera') {
                $('#radioCamera').iCheck('check');
            }
            else {
                $('#radioVideo').iCheck('check');
            }
            $('#cameraVideoUrl').val(path)
            console.log('threshold'+threshold);
            console.log('temporal_win'+temporal_win);
            if (threshold && temporal_win) {
                $('#temporalWin').val(temporal_win);
                $('#thresholdInput').val(threshold);
            }
        }
    }



    global.ModifyConfigStream = ModifyConfigStream;
    global.ModifyConfigStream.init();

}(window, jQuery));
