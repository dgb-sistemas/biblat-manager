$.noConflict();

jQuery(document).ready(function($) {

    "use strict";

    [].slice.call( document.querySelectorAll( 'select.cs-select' ) ).forEach( function(el) {
        new SelectFx(el);
    } );

    $('.selectpicker').selectpicker;


    $('#menuToggle').on('click', function(event) {
        $('body').toggleClass('open');
        $.ajax({url: $(this).data('url')});
    });

    $('.search-trigger').on('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        $('.search-trigger').parent('.header-left').addClass('open');
    });

    $('.search-close').on('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        $('.search-trigger').parent('.header-left').removeClass('open');
    });

    // $('.user-area> a').on('click', function(event) {
    // 	event.preventDefault();
    // 	event.stopPropagation();
    // 	$('.user-menu').parent().removeClass('open');
    // 	$('.user-menu').parent().toggleClass('open');
    // });

    $('.count').each(function () {
        $(this).prop('Counter',0).animate({
            Counter: $(this).text()
        }, {
            duration: 3000,
            easing: 'swing',
            step: function (now) {
                $(this).text(Math.ceil(now));
            }
        });
    });


    $('.alert[data-auto-dismiss]').each(function (index, element) {
        var $element = $(element),
            timeout  = $element.data('auto-dismiss') || 5000;

        setTimeout(function () {
            $element.alert('close');
        }, timeout);
    });

    $('form').submit(function(event) {
        $(this).find(':disabled').remove();
    });
    $("div[data-toggle=fieldset]").each(function() {
        var $this = $(this);

        //Add new entry
        $this.find("button[data-toggle=fieldset-add-row]").click(function() {
            var target = $($(this).data("target"));
            var oldrow = target.find("[data-toggle=fieldset-entry]:last");
            if (oldrow.is(':hidden')){
                oldrow.find(':input').prop("disabled", false);
                oldrow.closest("table").show();
            }else{
                var row = oldrow.clone(true, true);
                var elem_id = row.find(":input")[0].id;
                var elem_num = parseInt(elem_id.replace(/.*-(\d{1,4})-?.*/m, '$1')) + 1;
                console.log(elem_num)
                row.attr('data-id', elem_num);
                row.find(":input").each(function() {
                    var id = $(this).attr('id').replace('-' + (elem_num - 1), '-' + (elem_num));
                    $(this).attr('name', id).attr('id', id).val('').removeAttr("checked");
                });
                row.find("button[data-toggle=fieldset-remove-row]:hidden").show();
                row.show();
                oldrow.after(row);
            }
        }); //End add new entry

        //Remove row
        $this.find("button[data-toggle=fieldset-remove-row]").click(function() {
            var thisRow = $(this).closest("[data-toggle=fieldset-entry]");
            if($this.find("[data-toggle=fieldset-entry]").length > 1) {
                thisRow.remove();
            }else{
                thisRow.find(':input').prop("disabled", true);
                thisRow.closest("table").hide();
            }
        }); //End remove row
    });
});
