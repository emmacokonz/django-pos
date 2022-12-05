var Toast = Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
});

function toast(message='Error processing your request.', icon='error'){
  Toast.fire({
    title: message,
    icon: icon,
    timerProgressBar: true,
    timer: 9000,
  })
}

function change_parts_of_attr(id_attr){
  var split_str = id_attr.split('-');
  split_str[2]  = '';
  var newstring =split_str.join("-");
  return newstring
}

function set_currency(set=true){

  var myObjCurrency = {   style: "currency", currency: 'NGN', currencyDisplay:'code'}
  if(!set){
    myObjCurrency = ''
  }
  return myObjCurrency
}

function calculate_product_amount(qty, price){
  
  action_ = (parseFloat(qty) * parseFloat(price))
  
  if(action_ == '0'){
    action_ = "0.00"
  }else{
    action_ = action_
  }
  return Number(action_).toLocaleString("en-US", set_currency())
}

function removeComma(x){
 if (x) {
     if (x.length > 0) 
     {
      return x.replace(/,/g,'');
     }
  }
}

function removeCurrency(val, currency='NGN'){
  return val.replace( /^\NGN/, "" )
}

function sum_class(list,source){
  // source can be text for non input DOM elements or value for text inputs
  var total = 0;
  $(list).each(function() {
    
      if (source == 'text') {
        var val = $(this).text();
      }else{
        var val = $(this).val();
      }
    if(Number(val) != 0){
      clean_val = removeComma(removeCurrency(val,'NGN'));
      total += parseFloat(clean_val);
      
    }
  }); 
  return Number(total).toLocaleString("en-US", set_currency());
}

function empty_people_details(){
  return '<div>&nbsp;</div><div>&nbsp;</div><div>&nbsp;</div>'
}

function is_empty(selector, message=''){
  message = message !==''?message:"Fill all required field";
  if($(selector).val() == ''){
      toast(message);
      return true
  }else{
      return false
  }
}

$(document).ready(function(){
    //Initialize Select2 Elements
  $('.select2').select2();
  
  //autofocus select2 search
  $(document).on('select2:open', function(e) {
    document.querySelector(`[aria-controls="select2-${e.target.id}-results"]`).focus();
  });

  $('#invoice .invoice-quantity, #invoice .invoice-price').on('input', function(e){

    var obj = $(this);
    var obj_ref_parts = change_parts_of_attr(obj.attr('id'))
    price = $('#'+obj_ref_parts+'price').val();
    quantity = $('#'+obj_ref_parts+'quantity').val()
    if(price == ''){
      price = '0.00'
    }
    if(quantity == ''){
      quantity = '1'
    }
    $('#'+obj_ref_parts+'amount').text(calculate_product_amount(quantity,price))
    $("#subtotal").text(sum_class('.amount', 'text'))
  })

  $("#invoice .invoice-product").change(function(e){
    // Save the clicked element for reference.
    var obj = $(this);
    
    //set the price id reference.
    price = '#'+change_parts_of_attr(obj.attr('id'))+'price'
    //set the amount id reference.
    amount = '#'+change_parts_of_attr(obj.attr('id'))+'amount'
    //set the quantity id reference.
    quantity = '#'+change_parts_of_attr(obj.attr('id'))+'quantity'
    
    data = obj.serialize()+ '&product=' + obj.val(),
    //make ajax call to get the price of the items.
    $.ajax({
      type:'POST',
      url: invoice_vars.get_a_product_url,
      data: data,
      dataType: "json",
      headers: {'X-CSRFToken': window.CSRF_TOKEN},
      success: function(responds){
        if(responds['found'] == true){
          $(price).val(responds['price'])
          if($(price).val() == ''){
            $(price).val('0.00')
          }
          if($(quantity).val() == ''){
            $(quantity).val('1');
          }
          $(amount).text(calculate_product_amount($(quantity).val(),$(price).val()))
        }else{
          $(amount).text('0.00')
          $(quantity).val('')
          $(price).val('')
        }
        
        $('#subtotal').text(sum_class('.amount', 'text'))
        
      },
    })
  })

  $("#save_invoice, #save_print_invoice").click(function(e){
    //stop form normall action
    e.preventDefault();
    //check if the customer is selected
    data = $('#customer-name').serialize()+ '&subtotal=' + removeComma(removeCurrency($("#subtotal").text()))
    var count_data = 0;
    var total_quantity = 0;
    var products =[]
    var clickedObj = $(this)
    $(".invoice-product").each(function(e){
      
      var obj = $(this)
      if(obj.val() != ''){
        count_data += 1
        var base_selector_name = change_parts_of_attr(obj.attr('id'));
        product = obj.val();
        price = parseFloat($('#'+base_selector_name+'price').val())
        quantity = parseFloat($('#'+base_selector_name+'quantity').val());
        total_quantity += quantity
        each_invoice_product = JSON.stringify({"product":product,"quantity":quantity,"price":price})
        products.push(each_invoice_product)
      }
      
    });
    if(count_data == 0 | $('#customer-name').val()==''){
      if($('#customer-name').val()==''){
        toast('Please select a customer/vendor to continue.');
      }else if(count_data == 0){
        toast('Please add atleast one product before attempting save.');
      }
    }else{
      
      data = data + '&total_quantity=' + total_quantity+'&products='+ products +'&items='+count_data+"&date="+$('#invoice_at').val()+'&action=' + clickedObj.attr('id');
      
      url = invoice_vars.create_new_invoice;
        
      $.ajax({
        type:'POST',
        url: url,
        data: data,
        //contentType: "application/json; charset=utf-8",
        dataType: "json",
        headers: {'X-CSRFToken': window.CSRF_TOKEN},
        success: function(e){
          if(e['error'] == false){
            toast('Invoice created successfully.',"success"); 
            if(e['print'] == true){
              window.location.href = e['invoice_no'];
            }else{
              window.location.href = '/'+e['redirect'];
            }
          }
        },
      })
    }
  });

  
  $("#invoice #customer-name").change(function(e){
    // Save the clicked element for reference.
    var obj = $(this); 
    // serialize the data for sending the form data.
    var serializedData = obj.serialize();

    $.ajax({
      type:'POST',
      url: invoice_vars.get_a_person,
      data: serializedData,
      dataType: "json",
      headers: {'X-CSRFToken': window.CSRF_TOKEN},
      success: function(responds){
        if(responds['found'] == true){
          var address = responds['address'];
          var email = responds['email'];
          var phone = responds['phone'];
          $('#invoice #customer-details').html('<div>'+address+'</div><div>'+email+'</div><div>'+phone+'</div>')
        }else{
          $('#invoice #customer-details').html(empty_people_details())
          toast('Please choose a customer/vendor.')
        }
        
      },
      error: function(responds){
        
      },
    });
    //$("#update").html(data)
  });

  $('#account-type').change(function(e){
    if($(this).val() !== 'bank'){
      $('.openings').css('display','none')
      $('#opening-balance, #opening-balance-at').attr('disabled','disabled')
      $('#opening-balance, #opening-balance-at').attr('readonly','readonly')
    }else{
      $('.openings').css('display','block')
      $('#opening-balance, #opening-balance-at').removeAttr('disabled')
      $('#opening-balance, #opening-balance-at').removeAttr('readonly')
    }
  })
  
})
window.onpageshow = function(event) {
  if($('#account-type').val() !== 'bank'){
    $('.openings').css('display','none')
    $('#opening-balance, #opening-balance-at').attr('disabled','disabled')
    $('#opening-balance, #opening-balance-at').attr('readonly','readonly')
  }
  $(".invoice-product").each(function(e){
      var obj = $(this)
      id = change_parts_of_attr(obj.attr('id'))
      if(obj.val() != ''){
          amount = parseFloat($('#'+id+'quantity').val()) * parseFloat($('#'+id+'price').val());
          amount = Number(amount).toLocaleString("en-US", set_currency())
          $('.invoice-amount #'+id+'amount').text(amount)
        }else{
          $('.invoice-amount #'+id+'amount').text('0.00')
        }
        
  })

  $("#invoice .invoice-product").change( function(e){
      obj = $(this)
      var id_attr = obj.attr('id')
         var split_str = id_attr.split('-');
         split_str[2]  = '';
         id_attr ="#"+split_str.join("-");
      if(obj.val() == ''){
         $(id_attr+'DELETE').prop('checked',true)
      }else{
          $(id_attr+'DELETE').prop('checked',false)
      }
  })
};

