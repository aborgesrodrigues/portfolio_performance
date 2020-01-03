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
                var $id_start_date = $("#id_start_date")

                //The start date is needed to search for the stock market quotation
                if($id_start_date.val() == ""){
                    alert("Please inform the start date.");
                    $id_start_date.focus();
                    return;
                }

                //add a new allocation spot
                e.preventDefault();
                var $this = $(this);
                var formset = $("#formset");
                var form_template = formset.find(".allocation_form:first").clone();
                var html_template = form_template.html();
                var totalForms = $("#id_portfolio-TOTAL_FORMS").attr("autocomplete", "off");
                var nextIndex = parseInt(totalForms.val());
                totalForms.val(nextIndex + 1);
                html_template = replaceAll(html_template, "-0-", "-"+nextIndex+"-");
                var new_form = $("<div class='allocation_form'>"+html_template+"</div>");
                new_form.find(":input").each(function(e){
                    $(this).val("");
                });
                formset.append(new_form);
            });

            $(document).on('click', ".remove_allocation", function(e){
                $(this).parents(".allocation_form").remove();
                console.log($(this).parents(".allocation_form").length);
            });

            //Event fired when selected a stock in the autocomplete list
            $(document).on('change', '[data-autocomplete-light-function=select2]', function(e) {
                //get the stock selected
                var stock = $(e.target).find("option").val();
                var index = $(e.target).attr("id").replace("id_portfolio-", "").replace("-stock", "");

                if(stock){
                    //get the start date
                    var start_date = $("#id_start_date").val();
                    var formated_start_date = start_date.split("/")
                    formated_start_date = formated_start_date[2] + "-" + formated_start_date[1] + "-" + formated_start_date[0]
                    console.log("https://api.worldtradingdata.com/api/v1/history_multi_single_day?symbol=" + stock + "&date=" + formated_start_date + "&api_token=avDHLQfjNZUmiNJD6T0LOMq6MsAx7D61XiLYEDw2beXSbtFdwjKOd2QzLTNG");

                    //get the quotation of the stock on the start date
                    callAjax("https://api.worldtradingdata.com/api/v1/history_multi_single_day?symbol=" + stock + "&date=" + formated_start_date + "&api_token=avDHLQfjNZUmiNJD6T0LOMq6MsAx7D61XiLYEDw2beXSbtFdwjKOd2QzLTNG",
                        function(result){
                            if(result["date"]){
                                $("#id_portfolio-" + index + "-unit_value").val(result.data[stock].close);
                            }
                            else{
                                alert("There is no stock market quotation for the date '" + start_date + "'")
                            }
                        });
                }
            });

            //Event fired on the initialization of the stock autocomplete
            $(document).on('autocompleteLightInitialize', '[data-autocomplete-light-function=select2]', function() {
                window.__dal__tSelect2Initialized = true;

                //hide part of the autocomplete component
                $(this).siblings("[data-select2-id=1]").hide();
                $(this).siblings("[data-select2-id=2]").addClass("form-control");
                $(this).siblings("[data-select2-id=2]").css("width", "100%")
            });

            $(document).on('change', "[id$='desired_percentage']", function(e) {
                var percentage = parseInt($(e.target).val());
                var index = $(e.target).attr("id").replace("id_portfolio-", "").replace("-desired_percentage", "");

                if(percentage < 0 || percentage > 100){
                    alert("The percentage should be between 0 and 100.");
                    $(e.target).val("");
                    $(e.target).focus();
                }
                else{
                    //calculate the quantity needed to fulfill the percentage informed
                    var unit_value = parseFloat($("#id_portfolio-" + index + "-unit_value").val());
                    var balance = parseFloat(replaceAll($("#id_initial_balance").val(), ",", ""));
                    console.log(balance);
                    var desired_value = balance * percentage / 100;
                    var quantity = desired_value / unit_value;
                    var quantity_floor = Math.floor(quantity);

                    $("#id_portfolio-" + index + "-quantity").val(quantity_floor);
                    $("#id_portfolio-" + index + "-percentage").val((quantity_floor * unit_value / balance * 100).toFixed(2));
                }
            });

    });

    function calculate_percentage(element){

    }