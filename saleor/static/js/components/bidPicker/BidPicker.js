import _ from 'lodash';
import $ from 'jquery';
import classNames from 'classnames';
import { observer } from 'mobx-react';
import React, { Component, PropTypes } from 'react';

import AttributeSelectionWidget from './AttributeSelectionWidget';
import BidPriceInput from './BidPriceInput';
import Countdown from './Countdown';
import * as queryString from 'query-string';

@observer
export default class  BidPicker extends Component {

  static propTypes = {
    store: PropTypes.object.isRequired,
    urlGetPrice: PropTypes.string.isRequired,
    urlBidPrice: PropTypes.string.isRequired,
    urlAddCart: PropTypes.string.isRequired,
    variantAttributes: PropTypes.array.isRequired,
    variants: PropTypes.array.isRequired,
    end_bid: PropTypes.string.isRequired,
    max_price: PropTypes.number.isRequired,
    min_price: PropTypes.number.isRequired,
    product_id: PropTypes.number.isRequired,
    session_id: PropTypes.number.isRequired,
    onAddToCartSuccess: PropTypes.func.isRequired,
    onAddToCartError: PropTypes.func.isRequired
  }

  constructor(props) {
    super(props);
    const { variants } = this.props;

    const variant = variants.filter(v => !!Object.keys(v.attributes).length)[0];
    const params = queryString.parse(location.search);
    let selection = {};
    if (Object.keys(params).length) {
      Object.keys(params).some((name) => {
        const valueName = params[name];
        const attribute = this.matchAttributeBySlug(name);
        const value = this.matchAttributeValueByName(attribute, valueName);
        if (attribute && value) {
          selection[attribute.pk] = value.pk.toString();
        } else {
          // if attribute doesn't exist - show variant
          selection = variant ? variant.attributes : {};
          // break
          return true;
        }
      });
    } else if (Object.keys(variant).length) {
      selection = variant.attributes;
    }

    this.state = {
      errors: {},
      bid_price: this.props.min_price,
      selection: selection,
      current_price: this.props.min_price,
      isReady: false,
      winner: '',
      isEndSession: false,
      isWin: false,
      message: '',
      current_winner: false
    };
    this.matchVariantFromSelection();
  }

  componentWillMount() {
    this.handleReloadPrice();
    this.getNewestPrice();
  }

  handleBid = () => {
    const { store } = this.props;
    const bid_price  = parseInt(this.state.current_price) + 5000;
    if (bid_price > parseInt(this.props.min_price) && bid_price < parseInt(this.props.max_price) && !store.isEmpty) {
      $.ajax({
        url: this.props.urlBidPrice,
        method: 'post',
        data: {
          bid_price: bid_price,
          product_id: this.props.product_id,
          bid_session_id: this.props.session_id
        },
        success: (data) => {
          if(data.message)
          {
            this.setState({message: data.message})
          }
          this.handleReloadPrice();
        },
        error: (response) => {
        }
      });
    }
  }

  handleAddToCart = () => {
    const { store } = this.props;
    const quantity = 1
    if (quantity > 0 && !store.isEmpty) {
      $.ajax({
        url: this.props.urlAddCart,
        method: 'post',
        data: {
          quantity: quantity,
          variant: store.variant.id,
          bid_price: this.state.current_price
        },
        success: () => {
          this.props.onAddToCartSuccess();
        },
        error: (response) => {
          this.props.onAddToCartError(response);
        }
      });
    }
  }

  handleReloadPrice = () => {
    if(this.state.isEndSession == false) {
      $.ajax({
        url: this.props.urlGetPrice,
        method: 'get',
        data: {
          bid_session_id: this.props.session_id,
          product_id: this.props.product_id
        },
        success: (data) => {
          if (data.isEnd) {
            this.setState({isEndSession: true, isWin: data.isWin});
            if(data.isWin) {
              this.handleAddToCart();
            }

          } else {
            this.setState({current_price : data.current_price, isReady: true, winner: data.winner, current_winner: data.current_winner});            
          }

        },
        error: (response) => {
        }
      });
    } 
  }

  getNewestPrice = () => {
    setInterval(this.handleReloadPrice, 2000);  
    
  }

  handleAttributeChange = (attrId, valueId) => {
    this.setState({
      selection: Object.assign({}, this.state.selection, { [attrId]: valueId })
    }, () => {
      this.matchVariantFromSelection();
      let params = {};
      Object.keys(this.state.selection).forEach(attrId => {
        const attribute = this.matchAttribute(attrId);
        const value = this.matchAttributeValue(attribute, this.state.selection[attrId]);
        if (attribute && value) {
          params[attribute.slug] = value.slug;
        }
      });
      history.pushState(null, null, '?' + queryString.stringify(params));
    });
  }

  handleQuantityChange = (event) => {
    if (even.target.value <= bid_price){
      this.setState({bid_price: parseInt(event.target.value)});
    } 
  }

  matchAttribute = (id) => {
    const { variantAttributes } = this.props;
    const match = variantAttributes.filter(attribute => attribute.pk.toString() === id);
    return match.length > 0 ? match[0] : null;
  }

  matchAttributeBySlug = (slug) => {
    const { variantAttributes } = this.props;
    const match = variantAttributes.filter(attribute => attribute.slug === slug);
    return match.length > 0 ? match[0] : null;
  }

  matchAttributeValue = (attribute, id) => {
    const match = attribute.values.filter(attribute => attribute.pk.toString() === id);
    return match.length > 0 ? match[0] : null;
  }

  matchAttributeValueByName = (attribute, name) => {
    const match = attribute ? attribute.values.filter(value => value.slug === name) : [];
    return match.length > 0 ? match[0] : null;
  }

  matchVariantFromSelection() {
    const { store, variants } = this.props;
    let matchedVariant = null;
    variants.forEach(variant => {
      if (_.isEqual(this.state.selection, variant.attributes)) {
        matchedVariant = variant;
      }
    });
    store.setVariant(matchedVariant);
  }

  render() {
    const { store, variantAttributes } = this.props;
    const { errors, selection, quantity } = this.state;
    const disableAddToCart = store.isEmpty;

    const addToCartBtnClasses = classNames({
      'btn primary': true,
      'disabled': disableAddToCart
    });

    const noBorder = {
      border: 0
    };

    let alert_msg = <div></div>;
    let bid_result =  <div className="clearfix">
          <div className="form-group product__info__quantity">
            <label class="control-label product__variant-picker__label">Kết thúc trong</label>
            <Countdown
          end_bid={this.props.end_bid} />
          </div>
          <div className="form-group product__info__quantity">
            <label class="control-label product__variant-picker__label">Giá thầu hiện tại</label>
            <h4 class="form-control"> ₫ {this.state.current_price}</h4>
          </div>
        </div>;

    let bid_area =  <div className="clearfix">
          <BidPriceInput
            errors={errors.quantity}
            handleChange={this.handleQuantityChange}
            bid_price={this.props.bid_price}
            max_price={this.props.max_price}
            min_price={this.props.min_price}
            current_price={this.state.current_price}
            isReady={this.state.isReady}
          />
          <div className="form-group product__info__button">
            <button
              className={addToCartBtnClasses}
              onClick={this.handleBid}
              disabled={this.state.current_winner}>
              Đấu giá ngay
            </button>
          </div>
        </div>;

    if (this.state.isEndSession == true) {
      if(this.state.isWin) {
        alert_msg = <div className="alert alert-success" role="alert">Chúc mừng bạn đã là người chiến thắng, sản phẩm sẽ được đưa vào giỏ hàng.</div>;
      }
      else {
       alert_msg = <div className="alert alert-warning" role="alert">Chúc bạn may mắn lần sau</div>; 
      }

      bid_area = <div></div>;

      bid_result = <div></div>

    }

    let noti = <div></div>;
    if(this.state.current_winner) {
      noti = <div className="alert alert-info">{this.state.message}</div>
    }
    

    return (
      <div>
        {variantAttributes.map((attribute, i) =>
          <AttributeSelectionWidget
            attribute={attribute}
            handleChange={this.handleAttributeChange}
            key={i}
            selected={selection[attribute.pk]}
          />
        )}
        {bid_result}
        {bid_area}
        
        {noti}

        <div className="clearfix" style={{marginBottom: '10px'}}>Người chiến thắng hiện tại: <strong>{this.state.winner}</strong></div>
        {alert_msg}
      </div>
    );
  }
}
