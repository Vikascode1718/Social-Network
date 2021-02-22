import React, {useState} from 'react'
import axios from 'axios'

import InputField from '../../utils/InputField'

function SignUp() {
    const [first_name, setFirstName] = useState("");
    const [last_name, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [birthday, setBirthday] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState(true);
    const [apiResponse, setAPIResponse] = useState();

    var email_error = false;

    const handleSignUp = () => {
        let data = {};
        data['first_name'] = first_name;
        data['last_name'] = last_name;
        data['email'] = email;
        data['password'] = password;
        data['birthday'] = birthday;
        if (confirmPassword) {
            let config = { headers: {
                'Content-Type': 'application/json',}
            }
            axios.post('http://localhost:8000/api/person/signup',JSON.stringify(data), config)
                .then(function (response) {
                    let token = response.data.token;
                    // We got the token, yay!
                  }).catch(function (error) {
                    email_error = true;
                    let error_data = error.response.data;
                    let error_type, error_msg;
                    for (var k in error_data) {
                        error_type = k;
                        error_msg = error_data[k];
                        break;
                    }
                    let output_error = error_type + ": " + error_msg;
                    setAPIResponse(<div class="fw-bold text-uppercase text-danger text-sm">{output_error}</div>);
                  });
        }    
    };

    const handleFirstName = ({ target }) => {
        setFirstName(target.value);
    };

    const handleLastName = ({ target }) => {
        setLastName(target.value);
    };

    const handleEmail = ({ target }) => {
        setEmail(target.value);
    };

    const handlePassword = ({ target }) => {
        setPassword(target.value);
    };

    const handleConfirmPassword = ({ target }) => {
        if (password === target.value) {
            setConfirmPassword(true)
        }
        else { setConfirmPassword(false) }
    };

    const handleBirthday = ({ target }) => {
        setBirthday(target.value);
    };


    return (
        <div>
            <div className="mx-4 mt-5 fs-3 p-2">
                <span>Join Us Now!</span>
            </div>
            <div className="p-2 mx-4">
                <span>Already a member? <a href="#" className="text-decoration-none">Sign in</a></span>
            </div>
            <div className="row g-3 mb-5 mx-4">
                <div className="col-12">
                    <span className="text-sm text-muted">All fields are mandatory.</span>
                </div>
                <div className="col-md-6">
                    <InputField
                        label="First Name:"
                        onChange={handleFirstName}
                        name="first_name"
                        type="text" />
                </div>
                <div className="col-md-6">
                    <InputField
                        label="Last Name:"
                        onChange={handleLastName}
                        name="last_name"
                        type="text" />
                </div>
                {apiResponse}
                <div className="col-12">
                    <InputField
                        label="Email:"
                        onChange={handleEmail}
                        name="email"
                        type="email"
                        placeholder="you@company.com" />
                </div>
                <div className="col-md-6">
                    <InputField
                        label="Password:"
                        onChange={handlePassword}
                        name="password"
                        type="password" />
                </div>
                <div className="col-md-6">
                    <div className={confirmPassword ? '' : 'error-bg'}>
                        <InputField
                            label="Confirm Password:"
                            onChange={handleConfirmPassword}
                            name="confirm_password"
                            type="password" />
                    </div>
                </div>
                <div className="col-12">
                    <InputField
                        label="Birthday:"
                        onChange={handleBirthday}
                        name="birthday"
                        type="text"
                        placeholder="MM-DD-YYYY" />
                </div>
                <div className="col-12">
                    <div className="p-2"></div>
                    <div className="d-grid gap-2">
                        <button type="submit" onClick={handleSignUp} className="btn btn-primary text-sm fw-bold py-3">Let's Go!</button>
                    </div>
                </div>
            </div>
            <br/>
            <div className="text-muted text-sm tos-text-signup py-3">
                By clicking the button above, you agree to our <a href="#" className="text-decoration-none">terms of use</a> and <a href="#" className="text-decoration-none">privacy policies</a>
            </div>
        </div>
        );
}

export default SignUp;