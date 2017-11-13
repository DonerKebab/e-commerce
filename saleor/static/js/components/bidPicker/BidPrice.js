import classNames from 'classnames';
import React, { Component, PropTypes } from 'react';

export default class BidPriceInput extends Component {

  constructor(props) {
    super(props);
    static propTypes = {
      urlGetPrice = PropTypes.string.isRequired,
      bid_session_id = PropTypes.string.isRequired,
      product_id = PropTypes.string.isRequired
    }
    
    this.state = {
      current_price = 0
    }
  }

  onGetNewPriceSuccess = () => {
    return True
  }

  handleReloadPrice = () => {
      $.ajax({
        url: this.props.urlGetPrice,
        method: 'get',
        data: {
          bid_session_id: this.props.session_id,
          product_id: this.props.product_id
        },
        success: () => {
          onAddToCartSuccess();
        },
        error: (response) => {
          onAddToCartError(response);
        }
      });
  }



  render() {
    const { errors, bid_price, max_price, min_price} = this.props;
    const formGroupClasses = classNames({
      'form-group': true,
      'has-error': errors && !!errors.length,
      'product__info__quantity': true
    });
    return (
      <div className={formGroupClasses}>
        <label className="control-label product__variant-picker__label" htmlFor="id_quantity">{pgettext('Add to cart form field label', 'Quantity')}</label>
        <input
          className="form-control"
          defaultValue={bid_price}
          id="id_bid_price"
          max={parseInt(max_price)}
          min={min_price}
          step="10000"
          name="bid_price"
          onChange={this.props.handleChange}
          type="number"
          size="10"
        />
        {errors && (
          <span className="help-block">{errors.join(' ')}</span>
        )}
      </div>
    );
  }
}
