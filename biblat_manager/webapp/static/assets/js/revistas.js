jQuery(document).ready(function($) {
    let base_select = $('#base_datos')[0];
    let revista_select = $('#revista')[0];
    let disciplina_select = $('#disciplina')[0];
    let fasciculo_select = $('#fasciculo')[0];
    let fasciculo_value
    let disciplina_value
    if (fasciculo_select !== undefined)
        fasciculo_value = fasciculo_select.value
    if (disciplina_select !== undefined)
        disciplina_value = disciplina_select.value

    fn_disciplina = function(){
        base = base_select.value;

        fetch('/admin/disciplina/ajax_options/' + base).then(function (response) {
            response.json().then(function (data) {
                let optionHTML = ''
                for (let r of data.results){
                    optionHTML += '<option value="'+r.id+'"'+((disciplina_value==r.id)?'selected':'')+'>'+r.text+'</option>';
                }
                disciplina_select.innerHTML = optionHTML;
            });
        });
    }

    fn_disciplina_rev = function(){
        revista = revista_select.value;

        fetch('/admin/disciplina/ajax_options/rev/' + revista).then(function (response) {
            response.json().then(function (data) {
                let optionHTML = ''
                for (let r of data.results){
                    optionHTML += '<option value="'+r.id+'"'+((disciplina_value==r.id)?'selected':'')+'>'+r.text+'</option>';
                }
                disciplina_select.innerHTML = optionHTML;
            });
        });
    }

    fn_fasciculo = function(){
        revista = revista_select.value;

        fetch('/admin/fasciculo/ajax_options/' + revista).then(function (response) {
            response.json().then(function (data) {
                let optionHTML = ''
                for (let r of data.results){
                    optionHTML += '<option value="'+r.id+'"'+((fasciculo_value==r.id)?'selected':'')+'>'+r.text+'</option>';
                }
                fasciculo_select.innerHTML = optionHTML;
            });
        });
    }

    if (base_select != undefined){
        base_select.onchange = function () {
            fn_disciplina();
        }
        fn_disciplina();
    }

    if (revista_select != undefined) {
        revista_select.onchange = function () {
            fn_fasciculo();
            fn_disciplina_rev();
        }
        //fn_fasciculo();
        //fn_disciplina_rev();
    }
});