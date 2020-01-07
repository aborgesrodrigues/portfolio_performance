    function replaceAll(string, token, newtoken) {
        while (string.indexOf(token) != -1) {
            string = string.replace(token, newtoken);
        }
        return string;
    }

    function callAjax(url, retorno){
        $.ajax({
                type: "GET",
                url: url,
                async: false,
            }).done(function(data) {
                retorno(data);
            });
    }

    $( document ).ready(
        function()
        {
            $("[mask]").each(
                function()
                {
                    $(this).mask($(this).attr("mask"), {clearIfNotMatch: true, reverse: true});
                }
            );

            $(".selection").attr("display", "none");


            $("#add_allocation").on("click", function(e){
                if(validate_start_date()){

                    //add a new allocation spot
                    e.preventDefault();
                    var $this = $(this);
                    var formset = $("#formset");
                    var form_template = formset.find(".allocation_form:first").clone();
                    var html_template = form_template.html();
                    var totalForms = $("#id_allocations-TOTAL_FORMS").attr("autocomplete", "off");
                    var nextIndex = parseInt(totalForms.val());
                    totalForms.val(nextIndex + 1);
                    html_template = replaceAll(html_template, "-__prefix__-", "-"+nextIndex+"-");
                    var new_form = $("<div class='allocation_form'>"+html_template+"</div>");
                    new_form.find(":input").each(function(e){
                        $(this).val("");
                    });
                    formset.append(new_form);
                }
            });

            $(document).on('click', ".remove_allocation", function(e){
                $(this).parents(".allocation_form").remove();
            });

            $(document).on('change', "#id_start_date", function(e){
                update_unit_values();
            });

            $(document).on('change', "#id_initial_balance", function(e){
                //update the quantities of the stocks
                load_quantity_total();
            });

            //Event fired when selected a stock in the autocomplete list
            $(document).on('change', '[data-autocomplete-light-function=select2]', function(e) {
                var index = $(e.target).attr("id").replace("id_allocations-", "").replace("-stock", "");
                update_unit_value(index);

            });

            //Event fired on the initialization of the stock autocomplete
            $(document).on('autocompleteLightInitialize', '[data-autocomplete-light-function=select2]', function() {
                window.__dal__tSelect2Initialized = true;

                var $container = $(this).siblings(".select2-container--default");
                $container.addClass("form-control");
                $container.css("width", "100%")
            });

            //Event fired when the percentage of an allocation is changed
            $(document).on('change', "[id$='percentage']", function(e) {
                var percentage = parseInt($(e.target).val());
                var index = $(e.target).attr("id").replace("id_allocations-", "").replace("-percentage", "");
                var $initial_balance = $("#id_initial_balance")

                if(percentage < 0 || percentage > 100){
                    alert("The percentage should be between 0 and 100.");
                    $(e.target).val("");
                    $(e.target).focus();
                }
                else if(!$initial_balance.val()){
                    alert("Please inform the initial balance.");
                    $(e.target).val("");
                    $initial_balance.focus();
                }
                else if(validate_total_percentage(e.target)){
                    calculate_quantity_total(index, true);

                    calculate_residual();
                }
            });

            $("#btn_save").click(
                function(event){
                    //Remove disable attribute to allow saving the data
                    var $disableds = $(":disabled");
                    $disableds.attr("disabled", false);
                    $disableds.attr("readonly", true);
                    return true;
                });

            load_quantity_total();
            calculate_residual();

            var $container = $(".select2-container--default");
            $container.addClass("form-control");
            $container.css("width", "100%")
        });

    //validate if the sum of the percentages is less or equal 100
    function validate_total_percentage(element){
        var total_percentage = 0.0;
        $("[id$='percentage']").each(function(){
            //the element not visible is the template used to create the allocations form
            if($(this).is(":visible"))
                total_percentage += parseFloat($(this).val());
        });

        if(total_percentage > 100){
            alert("The sum of the percentages should not be more than 100.");
            if(element){
                $(element).val("");
                $(element).focus();
            }
            return false;
        }
        return true;
    }

    //Calculate the residual value
    function calculate_residual(){
        var $initial_balance = $("#id_initial_balance");
        if($initial_balance.val()){
            var initial_balance = parseFloat($initial_balance.val().replace(",", ""));

            $("[id$='total']").each(function(){
                //the element not visible is the template used to create the allocations form
                if($(this).is(":visible") && $(this).val())
                    initial_balance -= parseFloat($(this).val().replace(",", ""));
            });

            $("#id_residual").val(initial_balance.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,'))
        }
    }

    function load_quantity_total(){
        //calculate the quantity and total to all stocks
        $("[id$='unit_value']").each(function(){
            //the element not visible is the template used to create the allocations form
            if($(this).is(":visible") && $(this).val()){
                var index = $(this).attr("id").replace("id_allocations-", "").replace("-unit_value", "");
                calculate_quantity_total(index, false);
            }
        });
    }

    //Calculate the quantity and total to a specific stock
    function calculate_quantity_total(index, show_alert){
        var $percentage = $("#id_allocations-" + index + "-percentage");
        var $unit_value = $("#id_allocations-" + index + "-unit_value");
        var $balance = $("#id_initial_balance");

        if($balance.val() && $percentage.val() && $unit_value.val()){
            var percentage = parseFloat($percentage.val());
            var unit_value = parseFloat($unit_value.val());
            var balance = parseFloat(replaceAll($balance.val(), ",", ""));

            //Calculate the value to allocate in the selected stock
            var desired_value = balance * percentage / 100;
            //Calculate the quantity of stocks needed
            var quantity = desired_value / unit_value;
            var quantity_floor = Math.floor(quantity);

            $("#id_allocations-" + index + "-quantity").val(quantity_floor);
            $("#id_allocations-" + index + "-total").val((quantity_floor * unit_value).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,'));
        }
        else{
            if(show_alert){
                alert("The initial balance and unit value should be informed.")
            }
            $percentage.val("");
        }
    }

    function slugify(input)
    {
        input.value = input.value.toString().toLowerCase()
            .replace(/\s+/g, '-')           // Replace spaces with -
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\-\-+/g, '-')         // Replace multiple - with single -
            .replace(/^-+/, '')             // Trim - from start of text
            .replace(/-+$/, '');            // Trim - from end of text
    }

    function validate_start_date(){
        //The start date is needed to search for the stock market quotation
        var $id_start_date = $("#id_start_date")

        //The start date is needed to search for the stock market quotation
        if($id_start_date.val() == ""){
            alert("Please inform the start date.");
            $id_start_date.focus();
            return false;
        }

        return true;
    }

    function update_unit_values(){
        //Update unit value by the start date
        $("[id$='unit_value']").each(function(){
            //the element not visible is the template used to create the allocations form
            if($(this).is(":visible")){
                var index = $(this).attr("id").replace("id_allocations-", "").replace("-unit_value", "");
                update_unit_value(index);
            }
        });

        calculate_residual();
    }

    function update_unit_value(index){
        if(validate_start_date()){
            //get the stock selected
            var $stock = $("#id_allocations-" + index + "-stock");
            var stock = $stock.val();

            if(stock){
                //get the start date
                var start_date = $("#id_start_date").val();
                var formated_start_date = start_date.split("/")
                formated_start_date = formated_start_date[2] + "-" + formated_start_date[1] + "-" + formated_start_date[0]

                //get the quotation of the stock on the start date

                callAjax("/" + stock + "/" + formated_start_date,
                    function(result){
                        if(result["date"]){
                            $("#id_allocations-" + index + "-unit_value").val(result.data[stock].close);
                            calculate_quantity_total(index, false);
                        }
                        else{
                            alert("There is no stock market quotation for the date '" + start_date + "'")
                        }
                    });
            }
        }
    }