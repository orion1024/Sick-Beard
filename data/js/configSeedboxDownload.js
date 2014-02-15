$(document).ready(function(){

    $.fn.showHideProtocols = function() {
        
        $('.protocolDiv').each(function(){
            var providerName = $(this).attr('id');
            var selectedProvider = $('#configured_protocol :selected').val();

            if (selectedProvider+'Div' == providerName)
                $(this).show();
            else
                $(this).hide();

        });
    } 

    
    $.fn.refreshProviderList = function() {
            var idArr = $("#provider_order_list").sortable('toArray');
            var finalArr = new Array();
            $.each(idArr, function(key, val) {
                    var checked = + $('#enable_'+val).prop('checked') ? '1' : '0';
                    finalArr.push(val + ':' + checked);
            });

            $("#provider_order").val(finalArr.join(' '));
    }

    $('#configured_protocol').change(function(){
        $(this).showHideProtocols();
    });
    
    // initialization stuff

    $(this).showHideProtocols();


});
