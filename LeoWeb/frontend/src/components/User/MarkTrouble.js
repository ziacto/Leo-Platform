import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Redirect, Switch, Link, withRouter} from "react-router-dom";
import Message from '../../elements/Message';
import Error from '../../elements/Error';
import { COMMON_FIELDS, REGISTRATION_FIELDS, LOGIN_FIELDS, LOGIN_MESSAGE, ERROR_IN_LOGIN } from '../../MessageBundle';
import axios from 'axios';
import Button from '@material-ui/core/Button';
import 'bootstrap/dist/css/bootstrap.css';


/*
 * Class to implement marking toruble functionality for user
 */
export default class MarkTrouble extends Component {
	constructor(props) {
		super(props);
		this.onSubmit = this.onSubmit.bind(this);
		this.state = {
			user_name : this.props.user_name,
			latitude : 0,
			longitude : 0,
			status : 0
		};
	}

	onSubmit = async e => {
		
		e.preventDefault();
		const data = {
			token : localStorage.getItem('token'),
			latitude : this.state.latitude,
			longitude : this.state.longitude,
			user_name: this.props.user_name,
			type : "app",
			inTrouble : true
		};
		await axios.put('https://peaceful-refuge-01419.herokuapp.com/LeoHelp/user/mark_trouble', data)
		.then(response => {
			// console.log(response);
		})
		.catch(error => {
			console.log(error.response);
		});
		window.location.reload(false);
	}

	render() {	
		return (
			<div>
			<button onClick={this.onSubmit} className="btn markTrouble-btn">I'm in trouble</button>
			</div>
			);
		}
}
			