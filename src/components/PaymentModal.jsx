import { useState } from 'react';
import { FiSmartphone, FiCheck, FiX, FiLoader } from 'react-icons/fi';
import { useApi } from '../hooks/useApi';
import './PaymentModal.css';

export default function PaymentModal({ content, onClose, onSuccess }) {
  const { apiFetch } = useApi();
  const [step, setStep] = useState('phone'); // phone | otp | success
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpHint, setOtpHint] = useState('');
  const [paymentId, setPaymentId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const initiatePayment = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await apiFetch('/api/payments/initiate', {
        method: 'POST',
        body: JSON.stringify({ content_id: content.id, phone_number: phone })
      });
      setPaymentId(data.payment_id);
      setOtpHint(data.otp_hint);
      setStep('otp');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const confirmPayment = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await apiFetch('/api/payments/confirm', {
        method: 'POST',
        body: JSON.stringify({ payment_id: paymentId, otp })
      });
      setStep('success');
      setTimeout(() => onSuccess(), 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal payment-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            {step === 'phone' && '💳 Mobile Money Payment'}
            {step === 'otp' && '🔐 Enter OTP'}
            {step === 'success' && '✅ Payment Successful!'}
          </h2>
          <button className="modal-close" onClick={onClose}><FiX /></button>
        </div>

        <div className="payment-content-info">
          <p className="payment-title">{content.title}</p>
          <p className="payment-amount">UGX {Number(content.price).toLocaleString()}</p>
        </div>

        {error && <div className="payment-error">{error}</div>}

        {step === 'phone' && (
          <form onSubmit={initiatePayment}>
            <div className="input-group" style={{ marginBottom: 16 }}>
              <label>Phone Number</label>
              <div className="phone-input-wrap">
                <FiSmartphone className="phone-icon" />
                <input
                  type="tel"
                  className="input"
                  placeholder="07XX XXX XXX"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                  style={{ paddingLeft: 40 }}
                />
              </div>
            </div>
            <p className="payment-note">A confirmation code will be sent to your phone via SMS (simulated)</p>
            <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: 16 }} disabled={loading}>
              {loading ? <><FiLoader className="spin" /> Processing...</> : 'Pay Now'}
            </button>
          </form>
        )}

        {step === 'otp' && (
          <form onSubmit={confirmPayment}>
            {otpHint && <div className="otp-hint">{otpHint}</div>}
            <div className="input-group" style={{ marginBottom: 16 }}>
              <label>Confirmation Code (OTP)</label>
              <input
                type="text"
                className="input otp-input"
                placeholder="Enter 6-digit code"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                maxLength={6}
                required
                autoFocus
              />
            </div>
            <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: 8 }} disabled={loading}>
              {loading ? <><FiLoader className="spin" /> Confirming...</> : 'Confirm Payment'}
            </button>
          </form>
        )}

        {step === 'success' && (
          <div className="payment-success">
            <div className="success-icon"><FiCheck /></div>
            <p>Payment confirmed! Redirecting to your content...</p>
          </div>
        )}
      </div>
    </div>
  );
}
