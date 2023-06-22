jQuery.fn.extend({
    check: function() {
        return this.each(function() {
            this.checked = true;
        });
    },
    uncheck: function() {
        return this.each(function() {
            this.checked = false;
        });
    },
    disable: function() {
        return this.each(function() {
            $(this).addClass("disabled").addClass("processing");
            $(this).attr('disabled','disabled');
        });
    },
    enable: function() {
        return this.each(function() {
            $(this).removeClass("disabled").removeClass("processing");
            $(this).removeAttr('disabled');
        });
    },
    lockForm: function(){
        return this.each(function() {
            $(this).find("input,textarea").disable();
        });
    },
    unlockForm: function(){
        return this.each(function() {
            $(this).find("input,textarea").enable();
        });
    },
    processForm: function(successFunction,errorText, processText, failureFunction){
        return this.each(function() {
            var $form = $(this);
            var $submitButton = $form.find(".submit-btn");
            var originalText;

            processText = typeof processText !== 'undefined' ? processText : "<i class='fa fa-cog fa-spin'></i> processing";

            $form.validator().on('submit', function (e) {
                if (e.isDefaultPrevented()) {
                    // handle the invalid form...
                } else {
                    e.preventDefault();
                    // LOAD DATA FROM FORM
                    var url = $form.attr('action');
                    var data = $form.serialize();
                    originalText = $submitButton.html();
                    $submitButton.disable().html(processText);
                    $form.lockForm();
                    $.ajax({
                        url: url,
                        type: 'POST',
                        data: data,
                        success: successFunction,
                        error: function (jqXHR, textStatus, errorThrown) {

                            errorText = typeof errorText !== 'undefined' ? errorText : "There was an error while processing";

                            createSnackbar(errorText, 'Dismiss');
                            $form.unlockForm();
                            $submitButton.enable().html(originalText);
                            if(typeof failureFunction !== 'undefined'){
                                failureFunction(jqXHR.responseText);
                            }
                            if (jqXHR.status == 500) {
                                console.log('Internal error: ' + jqXHR.responseText);
                            } else {
                                console.log('Unexpected error.');
                            }
                        }
                    });
                }
            });

        });
    }
});