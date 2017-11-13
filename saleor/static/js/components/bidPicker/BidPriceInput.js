import classNames from 'classnames';
import React, { Component, PropTypes } from 'react';

export default class BidPriceInput extends Component {

  static propTypes = {
    errors: PropTypes.array,
    handleChange: PropTypes.func.isRequired,
    bid_price: PropTypes.number.isRequired,
    max_price: PropTypes.number.isRequired, // is product price
    min_price: PropTypes.number.isRequired, // is product start bid price
    current_price: PropTypes.number.isRequired,
    isReady: PropTypes.bool.isRequired

  }

  constructor(props) {
    super(props);
    this.state = {
      current_price: props.current_price,
      price_step: 5000
    }
  }

  componentWillReceiveProps(nextProps) {
    this.setState({ current_price: nextProps.current_price }); 
  }


  render() {
    const { errors, bid_price, max_price, min_price, current_price} = this.props;

    const formGroupClasses = classNames({
      'form-group': true,
      'has-error': errors && !!errors.length,
      'product__info__quantity': true
    });

    if(!this.props.isReady)
    {
      return (<div></div>)
    }
    else{
      
      let bidValue = 0;
      if ( parseInt(this.state.current_price) + this.state.price_step >= parseInt(this.props.max_price))
      {
        bidValue = this.props.max_price;
      }
      else {
        bidValue = parseInt(this.state.current_price) + this.state.price_step;
      }


      return (

      <div className={formGroupClasses}>
        <label className="control-label product__variant-picker__label" htmlFor="id_quantity">Đấu giá ngay:</label>
        <input
          className="form-control"
          value={bidValue}
          id="id_bid_price"
          name="bid_price"
          onChange={this.props.handleChange}
          type="text"
          size="10"
          style={{fontSize: '1.8rem'}}
          readOnly="true"
        />
        {errors && (
          <span className="help-block">{errors.join(' ')}</span>
        )}
      </div>
    );
    }

  }
}
