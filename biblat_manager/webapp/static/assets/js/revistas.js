jQuery(document).ready(function($) {
    let base_select = $('#base_datos')[0];
    let disciplina_select = $('#disciplina')[0];
    let disciplina_value = disciplina_select.value

    fnDisciplina = function(){
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

    base_select.onchange = function () {
        fnDisciplina();
    }

    fnDisciplina();
});