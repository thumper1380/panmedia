$(function () {
    // Setting
    var debug = true;

    // Fake AJAX request
    $.mockjax({
      url: '/api/tfa',
      dataType: 'json',
      response: function (settings) {
        this.responseText = {
          "ok": (Math.random() >= 0.5) // Random true/false
        };
      },
      responseTime: 1000
    });

    // Pincode
    var _pincode = [],
      _req = null;

    // Main form
    var $form = $('#form');

    // Pincode group
    var $group = $form.find('.form__pincode');

    // Submit button
    var $button = $form.find('a');

    // All input fields
    var $inputs = $group.find('input');

    // Event handler for input fields
    $inputs.on('keydown', function (event) {
      var input = $(this);
      var value = input.val().trim();

      if (event.keyCode === 9 || event.keyCode === 37 || event.keyCode === 38 || event.keyCode === 39 || event.keyCode === 40) {
        // Tab key or arrow keys pressed
        event.preventDefault();
        return;
      }

      if (event.keyCode === 8) {
        // Backspace key pressed
        if (value.length === 0) {
          var prevInput = input.prev('input');
          if (prevInput.length > 0) {
            prevInput.focus();
          }
        }
      }
    });


    // Event handler for input fields
    $inputs.on('input', function (event) {
      var input = $(this);
      var value = input.val().trim();

      // Only allow digits
      value = value.replace(/\D/g, '');
      input.val(value);

      if (value.length === 1) {
        var nextInput = input.next('input');
        if (nextInput.length > 0) {
          nextInput.val('').focus();
        } else {
          input.blur(); // Move focus away from the last input
          $button.focus();
        }
      }

      _pincode = $inputs.toArray().map(function (input) {
        return $(input).val().trim();
      });

      if (debug) {
        console.log('[onInput]', _pincode);
      }
    });

    // Event handler for form submission
    $form.on('submit', function (event) {
      event.preventDefault();

      // Handle each field
      $inputs.each(function () {
        // Disable field
        $(this).prop('disabled', true);
      });

      // Send request
      _req = $.ajax({
        type: 'POST',
        url: '/api/tfa',
        data: {
          'code': _pincode.join(''),
          '_csrf': ''
        }
      })
        .done(function (data, textStatus, jqXHR) {
          try {
            if (debug) {
              console.log('data', data);
            }
            if (data.ok === true) {
              $group.addClass('form__group--success');
            }
            if (data.ok === false) {
              $group.addClass('form__group--error');
            }
          } catch (err) {

          }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
          $group.removeClass('form__group--error');
        })
        .always(function (dataOrjqXHR, textStatus, jqXHRorErrorThrown) {
          // Reset pincode
          _pincode = [];

          // Reset request
          _req = null;

          setTimeout(function () {
            // Handle each field
            $inputs.each(function () {
              // Clear all fields
              $(this).val('');

              // Enable all fields
              $(this).prop('disabled', false);
            });

            // Remove response status class
            $group.removeClass('form__group--success form__group--error');

            // Disable submit button
            $button.attr('disabled', true);

            // Focus on first field
            $inputs.eq(0).focus();
          }, 2000);
        });

      if (debug) {
        console.log('[onSubmit]', _pincode);
      }
    });
  });

