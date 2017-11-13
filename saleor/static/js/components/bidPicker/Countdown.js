import classNames from 'classnames';
import React, { Component, PropTypes } from 'react';

export default class Countdown extends Component {

  static propTypes = {
    end_bid: PropTypes.string.isRequired
  }

  componentDidMount() {
  	var selected_date = new Date(this.props.end_bid);

	  // Update the count down every 1 second
	var x = setInterval(function() {

    // Get todays date and time
    var now = new Date().getTime();

    // Find the distance between now an the count down date
    var distance = selected_date - now;

    // Time calculations for days, hours, minutes and seconds
    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    if(minutes < 10)
    {
      minutes = "0" + minutes;
    }

    if(seconds < 10)
    {
      seconds = "0" + seconds;
    }

    // Display the result in the element with id="demo"
      document.getElementById("countdown").innerHTML = hours + ":" + minutes + ":" + seconds;
    // If the count down is finished, write some text 
    if (distance < 0) {
      clearInterval(x);
      document.getElementById("countdown").innerHTML = "EXPIRED";
    }
  }, 1000);
  }

  

  render() {
  	const redText = {
	  color : 'rgb(204, 51, 85)'
	};
    return (
        <h4 id="countdown" class="form-control" style={redText}></h4>
    );
  }
}
