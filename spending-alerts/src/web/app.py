from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import logging
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For session management

# Configure logging with more detailed format and console handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Hardcoded user data (in real app, this would be in a database)
USERS = {
    'user1': {
        'password': 'password123',
        'name': 'John Doe',
        'balance': 100000000.00,  # $100,000,000
        'account_number': '1234567890',
        'transactions': []
    }
}

ANOMALY_THRESHOLD = 5000  # Amount above which is considered anomalous

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logger.info(f"Login attempt for user: {username}")
        
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            logger.info(f"✅ Login successful: User='{username}'")
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"❌ Failed login attempt: User='{username}'")
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_data = USERS[session['user']]
    recent_transactions = sorted(user_data['transactions'], 
                              key=lambda x: x['timestamp'], 
                              reverse=True)[:5]
    return render_template('dashboard.html', 
                         user_data=user_data,
                         recent_transactions=recent_transactions)

@app.route('/transaction', methods=['GET', 'POST'])
@login_required
def transaction():
    alert = None
    if request.method == 'POST':
        try:
            to_account = request.form['to_account']
            amount = float(request.form['amount'])
            description = request.form.get('description', '')
            confirm = request.form.get('confirm_anomaly', 'false') == 'true'
            user_data = USERS[session['user']]
            
            logger.info(f"Processing transaction request: Amount=${amount:,.2f}, To={to_account}")
            
            # Check for insufficient funds first
            if amount > user_data['balance']:
                message = f"Insufficient funds: Balance=${user_data['balance']:,.2f}, Attempted=${amount:,.2f}"
                logger.warning(f"❌ {message} User='{session['user']}'")
                flash("Insufficient funds in your account!", 'danger')
                return render_template('transaction.html', 
                    alert=f"❌ Transaction blocked: Your balance (${user_data['balance']:,.2f}) is insufficient for this transfer")
            
            # Check for anomaly
            if amount > ANOMALY_THRESHOLD and not confirm:
                message = f"ANOMALY ALERT: Transaction amount ${amount:,.2f} exceeds limit of ${ANOMALY_THRESHOLD:,.2f}!"
                logger.warning(f"⚠️ {message} User='{session['user']}', To='{to_account}'")
                flash(message, 'warning')
                # Return the same form with confirmation option
                return render_template('transaction.html', 
                    show_confirmation=True,
                    to_account=to_account,
                    amount=amount,
                    description=description,
                    alert=f"⚠️ Large transaction detected: ${amount:,.2f} exceeds the normal limit of ${ANOMALY_THRESHOLD:,.2f}. Please confirm to proceed.")
            
            # Process transaction
            previous_balance = user_data['balance']
            user_data['balance'] -= amount
            transaction_data = {
                'timestamp': datetime.now(),
                'type': 'transfer',
                'amount': amount,
                'to_account': to_account,
                'description': description,
                'balance_after': user_data['balance']
            }
            user_data['transactions'].append(transaction_data)
            
            # Log based on whether it was an anomaly or not
            if amount > ANOMALY_THRESHOLD:
                logger.warning(f"✅⚠️ Large transaction confirmed: User='{session['user']}' Amount=${amount:,.2f} To='{to_account}' Balance: ${previous_balance:,.2f} -> ${user_data['balance']:,.2f}")
                flash(f"Large transaction of ${amount:,.2f} completed successfully!", 'success')
            else:
                logger.info(f"✅ Transaction successful: User='{session['user']}' Amount=${amount:,.2f} To='{to_account}' Balance: ${previous_balance:,.2f} -> ${user_data['balance']:,.2f}")
                flash(f"Successfully transferred ${amount:,.2f} to {to_account}", 'success')
            
            return redirect(url_for('dashboard'))
                
        except ValueError as e:
            logger.error(f"Invalid amount entered by user '{session['user']}'")
            flash("Please enter a valid amount", 'danger')
            return render_template('transaction.html', alert="Invalid amount entered")
            
    return render_template('transaction.html', alert=alert)

@app.route('/history')
@login_required
def history():
    user_data = USERS[session['user']]
    transactions = sorted(user_data['transactions'], 
                        key=lambda x: x['timestamp'], 
                        reverse=True)
    return render_template('history.html', transactions=transactions)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
