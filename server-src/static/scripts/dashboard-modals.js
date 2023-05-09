class phModalBox {
	constructor(selector) {
		this.maxPhUp = 10;
		this.maxPhDown = 10;
		this.phIncrement = 0.5;
		this.elem = document.querySelector(selector);
		this.dispenseButton = document.querySelector('#dispense-ph-button');
		this.bodyText = document.querySelector('.ph-modal-body p');
		this.upControls = new controlButtonGrp('#ph-up-plus', '#ph-up-minus', '#ph-up-text', 0, this.maxPhUp, this.phIncrement, this.updateDispenseButton.bind(this));
		this.downControls = new controlButtonGrp('#ph-down-plus', '#ph-down-minus', '#ph-down-text', 0, this.maxPhDown, this.phIncrement, this.updateDispenseButton.bind(this));
		this.setupEvents();
	}
	
	show() {
		this.upControls.setValue(0);
		this.downControls.setValue(0);
		this.elem.classList.toggle('is-active');
		this.onShow()
	}
	
	close() {
		this.elem.classList.toggle('is-active');
		this.onClose();
	}

	changeRequested() {
		return this.upControls.value + this.downControls.value > 0;
	}

	updateDispenseButton() {
		if (this.changeRequested()) {
			this.dispenseButton.removeAttribute('disabled');
		} else {
			this.dispenseButton.setAttribute('disabled', 'disabled');
		};
	}
	
	setupEvents() {
	  	// Cancel button, background
		const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
		modalClose.forEach((e) => {
			e.addEventListener("click", () => {
				this.close();
			})
		});

	  	// Dispense button
		this.dispenseButton.addEventListener("click", () => {
			const [requestData, confirmString] = this.makeRequest();
			this.close();
			confirmModal.show(requestData, confirmString);
		});
	}

	makeRequest() {
		let requestData = [];
		let confirmString = '';

		if (this.changeRequested()) {
			if (this.upControls.value > 0) {
				let upRequest = {"ph": {"status": "request"}};
				upRequest["ph"]["action"] = "up";
				upRequest["ph"]["value"] = this.upControls.value;
				requestData.push(upRequest);
				confirmString += `Dispense ${this.upControls.value} mL of pH Up`;
			};
			if (this.downControls.value > 0) {
				let downRequest = {"ph": {"status": "request"}};
				downRequest["ph"]["action"] = "down";
				downRequest["ph"]["value"] = this.downControls.value;
				requestData.push(downRequest);
				if (confirmString.length > 0) {
					confirmString += '<br />'
				}
				confirmString += `Dispense ${this.downControls.value} mL of pH Down`
			}
		};
		return [requestData, confirmString]
	}

	onShow() {
		const event = new Event('modal:show');
		this.elem.dispatchEvent(event);
	}

	onClose() {
		const event = new Event('modal:close');
		this.elem.dispatchEvent(event);
	}
};

class ecModalBox {
	constructor(selector) {
		this.ecAmounts = [0, 0, 0, 0];
		this.maxAmounts = [150, 150, 150, 150];
		this.requestNames = ['nute1', 'nute2', 'nute3', 'nute4', 'nute5'];
		this.displayNames = ['FloraGro', 'FloraMicro', 'FloraBloom', 'CALiMAGic'];
		this.ecIncrement = 5;
		this.elem = document.querySelector(selector);
		this.dispenseButton = document.querySelector('#dispense-ec-button');
		this.bodyText = document.querySelector('.ec-modal-body p');
		this.ecOneText = document.querySelector('#ec-one-text');
		this.ecOnePlus = document.querySelector('#ec-one-plus');
		this.ecOneMinus = document.querySelector('#ec-one-minus');
		this.ecTwoText = document.querySelector('#ec-two-text');
		this.ecTwoPlus = document.querySelector('#ec-two-plus');
		this.ecTwoMinus = document.querySelector('#ec-two-minus');
		this.ecThreeText = document.querySelector('#ec-three-text');
		this.ecThreePlus = document.querySelector('#ec-three-plus');
		this.ecThreeMinus = document.querySelector('#ec-three-minus');
		this.ecFourText = document.querySelector('#ec-four-text');
		this.ecFourPlus = document.querySelector('#ec-four-plus');
		this.ecFourMinus = document.querySelector('#ec-four-minus');
		this.textAreas = [this.ecOneText, this.ecTwoText, this.ecThreeText, this.ecFourText];
		this.plusButtons = [this.ecOnePlus, this.ecTwoPlus, this.ecThreePlus, this.ecFourPlus];
		this.minusButtons = [this.ecOneMinus, this.ecTwoMinus, this.ecThreeMinus, this.ecFourMinus];
		this.setupEvents();
	}
	
	show() {
		this.elem.classList.toggle('is-active');
		this.onShow()
	}
	
	close() {
		this.ecAmounts = [0, 0, 0, 0];
		this.textAreas.forEach((area) => {
			area.value = '';
		});
		this.minusButtons.forEach((btn) => {
			btn.setAttribute('disabled', 'disabled');
		});
		this.plusButtons.forEach((btn) => {
			btn.removeAttribute('disabled');
		});
		this.dispenseButton.setAttribute('disabled', 'disabled');
		this.elem.classList.toggle('is-active');
		this.onClose();
	}

	setupEvents() {
	  // Cancel button, background
		const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
		modalClose.forEach((e) => {
			e.addEventListener("click", () => {
				this.close();
			})
		});

	  // Dispense button
		this.dispenseButton.addEventListener("click", () => {
			const [requestData, confirmString] = this.makeRequest();
			this.close();
			confirmModal.show(requestData, confirmString);
		});

	  // + and - buttons
		this.ecOnePlus.addEventListener("click", () => {
			this.onEcOnePlus();
		});

		this.ecOneMinus.addEventListener("click", () => {
			this.onEcOneMinus();
		});

		this.ecTwoPlus.addEventListener("click", () => {
			this.onEcTwoPlus();
		});

		this.ecTwoMinus.addEventListener("click", () => {
			this.onEcTwoMinus();
		});

		this.ecThreePlus.addEventListener("click", () => {
			this.onEcThreePlus();
		});

		this.ecThreeMinus.addEventListener("click", () => {
			this.onEcThreeMinus();
		});

		this.ecFourPlus.addEventListener("click", () => {
			this.onEcFourPlus();
		});

		this.ecFourMinus.addEventListener("click", () => {
			this.onEcFourMinus();
		});

		// Text boxes (ensure only numbers)
		this.ecOneText.addEventListener("blur", () => {
			this.ecAmounts[0] = validateNumber(this.ecOneText.value);
			this.updateOne();
		});

		this.ecTwoText.addEventListener("blur", () => {
			this.ecAmounts[1] = validateNumber(this.ecTwoText.value);
			this.updateTwo();
		});

		this.ecThreeText.addEventListener("blur", () => {
			this.ecAmounts[2] = validateNumber(this.ecThreeText.value);
			this.updateThree();
		});

		this.ecFourText.addEventListener("blur", () => {
			this.ecAmounts[3] = validateNumber(this.ecFourText.value);
			this.updateFour();
		});
	}

	updateDispenseButton() {
		const amountSum = this.ecAmounts.reduce((partialSum, a) => partialSum + a, 0);
		if (amountSum > 0) {
			this.dispenseButton.removeAttribute('disabled');
		} else {
			this.dispenseButton.setAttribute('disabled', 'disabled');
		}
	}

	onEcOnePlus() {
		this.ecAmounts[0] = Math.min(this.maxAmounts[0], this.ecAmounts[0] + this.ecIncrement);
		this.updateOne();
	}

	onEcOneMinus() {
		this.ecAmounts[0] = Math.max(0, this.ecAmounts[0] - this.ecIncrement);
		this.updateOne();
	}

	updateOne() {
	  	// Clip values between 0 and this.maxAmounts[0], enable/disable buttons, etc
		if (this.ecAmounts[0] > 0) {
			this.ecAmounts[0] = Math.min(this.ecAmounts[0], this.maxAmounts[0]);
			if (this.ecAmounts[0] == this.maxAmounts[0]) {
				this.ecOnePlus.setAttribute('disabled', 'disabled');
			} else {
				this.ecOnePlus.removeAttribute('disabled');
			};
			this.ecOneMinus.removeAttribute('disabled');
			this.ecOneText.value = this.ecAmounts[0];
		} else {
			this.ecOnePlus.removeAttribute('disabled');
			this.ecOneMinus.setAttribute('disabled', 'disabled');
			this.ecOneText.value = '';
		};
		this.updateDispenseButton();
	}

	onEcTwoPlus() {
		this.ecAmounts[1] = Math.min(this.maxAmounts[1], this.ecAmounts[1] + this.ecIncrement);
		this.updateTwo();
	}

	onEcTwoMinus() {
		this.ecAmounts[1] = Math.max(0, this.ecAmounts[1] - this.ecIncrement);
		this.updateTwo();
	}

	updateTwo() {
	  // Clip values between 0 and this.maxAmounts[1], enable/disable buttons, etc
		if (this.ecAmounts[1] > 0) {
			this.ecAmounts[1] = Math.min(this.ecAmounts[1], this.maxAmounts[1]);
			if (this.ecAmounts[1] == this.maxAmounts[1]) {
				this.ecTwoPlus.setAttribute('disabled', 'disabled');
			} else {
				this.ecTwoPlus.removeAttribute('disabled');
			};
			this.ecTwoMinus.removeAttribute('disabled');
			this.ecTwoText.value = this.ecAmounts[1];
		} else {
			this.ecTwoPlus.removeAttribute('disabled');
			this.ecTwoMinus.setAttribute('disabled', 'disabled');
			this.ecTwoText.value = '';
		};
		this.updateDispenseButton();
	}

	onEcThreePlus() {
		this.ecAmounts[2] = Math.min(this.maxAmounts[2], this.ecAmounts[2] + this.ecIncrement);
		this.updateThree();
	}

	onEcThreeMinus() {
		this.ecAmounts[2] = Math.max(0, this.ecAmounts[2] - this.ecIncrement);
		this.updateThree();
	}

	updateThree() {
	  // Clip values between 0 and this.maxAmounts[2], enable/disable buttons, etc
		if (this.ecAmounts[2] > 0) {
			this.ecAmounts[2] = Math.min(this.ecAmounts[2], this.maxAmounts[2]);
			if (this.ecAmounts[2] == this.maxAmounts[2]) {
				this.ecThreePlus.setAttribute('disabled', 'disabled');
			} else {
				this.ecThreePlus.removeAttribute('disabled');
			};
			this.ecThreeMinus.removeAttribute('disabled');
			this.ecThreeText.value = this.ecAmounts[2];
		} else {
			this.ecThreePlus.removeAttribute('disabled');
			this.ecThreeMinus.setAttribute('disabled', 'disabled');
			this.ecThreeText.value = '';
		};
		this.updateDispenseButton();
	}

	onEcFourPlus() {
		this.ecAmounts[3] = Math.min(this.maxAmounts[3], this.ecAmounts[3] + this.ecIncrement);
		this.updateFour();
	}

	onEcFourMinus() {
		this.ecAmounts[3] = Math.max(0, this.ecAmounts[3] - this.ecIncrement);
		this.updateFour();
	}

	updateFour() {
	  // Clip values between 0 and this.maxAmounts[3], enable/disable buttons, etc
		if (this.ecAmounts[3] > 0) {
			this.ecAmounts[3] = Math.min(this.ecAmounts[3], this.maxAmounts[3]);
			if (this.ecAmounts[3] == this.maxAmounts[3]) {
				this.ecFourPlus.setAttribute('disabled', 'disabled');
			} else {
				this.ecFourPlus.removeAttribute('disabled');
			};
			this.ecFourMinus.removeAttribute('disabled');
			this.ecFourText.value = this.ecAmounts[3];
		} else {
			this.ecFourPlus.removeAttribute('disabled');
			this.ecFourMinus.setAttribute('disabled', 'disabled');
			this.ecFourText.value = '';
		};
		this.updateDispenseButton();
	}

	makeRequest() {
		let requestData = [];
		let confirmString = '';

		const amountSum = this.ecAmounts.reduce((partialSum, a) => partialSum + a, 0);
		if (amountSum > 0) {
		// Do this because the variable `this` is not in scope in the mapped function
			const requestNames = this.requestNames;
			const displayNames = this.displayNames;
			this.ecAmounts.map(function(amount, i) {
				if (amount > 0) {
					let ecRequest = {"ec": {"status": "request"}};
					ecRequest["ec"]["action"] = requestNames[i];
					ecRequest["ec"]["value"] = amount;
					requestData.push(ecRequest);
					if (confirmString.length > 0) {
						confirmString += '<br />'
					};
					confirmString += `Dispense ${amount} mL of ${displayNames[i]}`;
				}
			});
		};
		return [requestData, confirmString]
	}

	onShow() {
		const event = new Event('modal:show');
		this.elem.dispatchEvent(event);
	}

	onClose() {
		const event = new Event('modal:close');
		this.elem.dispatchEvent(event);
	}

	addEventListener(event, callback) {
		this.elem.addEventListener(event, callback);
	}
};

class levelModalBox {
	constructor(selector) {
		this.maxGallons = 7;
		this.elem = document.querySelector(selector);
		this.dispenseButton = document.querySelector('#dispense-level-button');
		this.bodyText = document.querySelector('.level-modal-body p');
		this.fillButton = document.querySelector("#fill-button")
		this.drainButton = document.querySelector("#drain-button")
		this.controls = new controlButtonGrp('#level-plus', '#level-minus', '#level-text', 0, this.maxGallons, 0.1, this.updateDispenseButton.bind(this), false);
		this.setupEvents();
	}
	
	show() {
		this.controls.setValue(current_level);
		this.elem.classList.toggle('is-active');
		this.onShow()
	}
	
	close() {
		this.elem.classList.toggle('is-active');
		this.onClose();
	}
	
	setupEvents() {
		const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
		modalClose.forEach((e) => {
			e.addEventListener("click", () => {
				this.close();
			});
		});

		this.fillButton.addEventListener("click", () => {
			this.controls.setValue(7);
		});

		this.drainButton.addEventListener("click", () => {
			this.controls.setValue(0);
		});

		this.dispenseButton.addEventListener("click", () => {
			const [requestData, confirmString] = this.makeRequest();
			this.close();
			confirmModal.show(requestData, confirmString);
		});
	}

	updateDispenseButton() {
		if (this.controls.value != current_level) {
			this.dispenseButton.removeAttribute('disabled');
		} else {
			this.dispenseButton.setAttribute('disabled', 'disabled');
		};
	}

	makeRequest() {
		let requestData = [];
		let confirmString = '';

		if (this.controls.value != current_level) {
			if (this.controls.value === 0) {
				confirmString = "Empty the reservoir";
			} else if (this.controls.value === this.maxGallons) {
				confirmString = "Fill the reservoir";
			} else {
				confirmString = `Set the water level to ${this.controls.value} gallons`
			};
			requestData.push({"level": {"status": "request", "action": "set", "value": this.controls.value}})
		};
		return [requestData, confirmString]
	}
	
	onShow() {
		const event = new Event('modal:show');
		this.elem.dispatchEvent(event);
	}
	
	onClose() {
		const event = new Event('modal:close');
		this.elem.dispatchEvent(event);
	}
};

class confirmModalBox {
	constructor(selector, postEndpoint) {
		this.elem = document.querySelector(selector);
		this.confirmButton = document.querySelector('.modal-card-foot .confirm-button');
		this.bodyText = document.querySelector('#confirm-string');
		this.postEndpoint = postEndpoint;
		this.setupButtons();
	}
	
	show(postData, confirmString) {
		this.postData = postData;
		this.bodyText.innerHTML = confirmString;
		this.elem.classList.toggle('is-active');
		this.onShow()
	}

	close() {
		this.elem.classList.toggle('is-active');
		this.onClose();
	}

	setupButtons() {
		const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
		this.confirmButton.addEventListener("click", () => {
			this.sendFlagPost();
		});
		const that = this;
		modalClose.forEach((e) => {
			e.addEventListener("click", () => {
				that.elem.classList.toggle('is-active');
				const event = new Event('modal:close');
				that.elem.dispatchEvent(event);
			})
		})
	}

	sendFlagPost() {
		let method = 'POST'
		return fetch(this.postEndpoint, {
			'method': method,
			'headers': {
				"Content-Type": "application/json"
			},
			'body': JSON.stringify(this.postData)
		})
		.then(response => {
			if (response.status === 200) {
			  // Just close the modal :)
				this.elem.classList.toggle('is-active');
				const event = new Event('modal:close');
				this.elem.dispatchEvent(event);
			};
		});
	}

	onShow() {
		const event = new Event('modal:show');
		this.elem.dispatchEvent(event);
	}

	onClose() {
		const event = new Event('modal:close');
		this.elem.dispatchEvent(event);
	}
};

class controlButtonGrp {
	constructor(plusSelector, minusSelector, textSelector, minVal, maxVal, increment, updateCallback, resetOnMin=true) {
		this.plus = document.querySelector(plusSelector);
		this.minus = document.querySelector(minusSelector);
		this.text = document.querySelector(textSelector);
		this.value = 0;
		this.minVal = minVal;
		this.maxVal = maxVal;
		this.increment = increment;
		this.updateCallback = updateCallback;
		this.validNumberPattern = new RegExp(/^\d*\.?\d+/);
		this.resetOnMin = resetOnMin;
		this.setupEvents();
	}

	validateNumberEntry(newValue) {
		if (this.validNumberPattern.test(newValue)) {
			return parseFloat(newValue);
		} else {
			return 0;
		};
	}

	setupEvents() {
		this.plus.addEventListener("click", () => {
			this.onPlus();
		});

		this.minus.addEventListener("click", () => {
			this.onMinus();
		});

		this.text.addEventListener("blur", () => {
			this.value = this.validateNumberEntry(this.text.value);
			this.updateText();
		});
	}

	reset() {
		this.value = 0;
		this.updateText();
	}

	setValue(newValue) {
		this.value = newValue;
		this.updateText();
	}

	onPlus() {
		this.value = Math.min(this.maxVal, this.value + this.increment);
		this.updateText();
	}

	onMinus() {
		this.value = Math.max(this.minVal, this.value - this.increment);
		this.updateText();
	}

	updateText() {
		if (this.value > this.minVal) {
			this.value = Math.round(100 * Math.min(this.value, this.maxVal)) / 100;
			if (this.value == this.maxVal) {
				this.plus.setAttribute('disabled', 'disabled');
			} else {
				this.plus.removeAttribute('disabled');
			};
			this.minus.removeAttribute('disabled');
			this.text.value = this.value;
		} else {
			this.plus.removeAttribute('disabled');
			this.minus.setAttribute('disabled', 'disabled');
			if (this.resetOnMin) {
				this.text.value = '';
			} else {
				this.text.value = this.value;
			};
		};
		this.updateCallback();
	}
};

const validNumber = new RegExp(/^\d*\.?\d+/);
const validateNumber = (newValue) => {
	if (validNumber.test(newValue)) {
		return parseFloat(newValue);
	} else {
		return 0;
	};
};

// Setup modals and enable buttons to open them
const phModal = new phModalBox("#phModal");
const ecModal = new ecModalBox("#ecModal");
const levelModal = new levelModalBox("#levelModal");
const confirmModal = new confirmModalBox("#confirmModal", postEndpoint)

document.querySelector("#phBox").addEventListener("click", e => {
	phModal.show();}
	);
document.querySelector("#ecBox").addEventListener("click", e => {
	ecModal.show();}
	);
document.querySelector("#levelBox").addEventListener("click", e => {
	levelModal.show();}
	);
