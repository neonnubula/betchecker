import React, { useState } from "react";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const ApplyForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    interest: "",
    message: ""
  });
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Validation functions
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone: string): boolean => {
    // International phone format - allows +, spaces, dashes, parentheses, and 7-15 digits
    const phoneRegex = /^\+?[1-9][\d]{0,15}$/;
    const cleanPhone = phone.replace(/[\s-()]/g, '');
    return phoneRegex.test(cleanPhone) && cleanPhone.length >= 7 && cleanPhone.length <= 15;
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!validateEmail(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.phone.trim()) {
      newErrors.phone = "Phone number is required";
    } else if (!validatePhone(formData.phone)) {
      newErrors.phone = "Please enter a valid phone number";
    }

    if (!formData.interest) {
      newErrors.interest = "Please select your interest level";
    }

    if (!formData.message.trim()) {
      newErrors.message = "Please tell us what you're interested in testing";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: "" }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error("Please fix the errors below");
      return;
    }

    setSubmitting(true);
    
    try {
      const response = await fetch('/api/submit-application', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit application');
      }

      const result = await response.json();
      
      toast.success("Application submitted successfully! Check your email for confirmation.");
      setFormData({ name: "", email: "", phone: "", interest: "", message: "" });
      setErrors({});
      
    } catch (error) {
      console.error('Submission error:', error);
      toast.error("Failed to submit application. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <h2 className="text-xl font-display font-bold mb-6 text-center text-gray-900">Apply for Early Access as a Tester</h2>
      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
        <div className="flex-1">
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name *</label>
          <input
            id="name"
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className={`mt-1 w-full rounded-xl border px-3 py-2 focus:outline-none focus:ring-2 ${
              errors.name 
                ? 'border-red-300 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-pulse-500'
            }`}
          />
          {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
        </div>
        
        <div className="flex-1">
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email address *</label>
          <input
            id="email"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            className={`mt-1 w-full rounded-xl border px-3 py-2 focus:outline-none focus:ring-2 ${
              errors.email 
                ? 'border-red-300 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-pulse-500'
            }`}
          />
          {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
        </div>
        
        <div className="flex-1">
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Phone Number *</label>
          <input
            id="phone"
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="+1 234 567 8900"
            required
            className={`mt-1 w-full rounded-xl border px-3 py-2 focus:outline-none focus:ring-2 ${
              errors.phone 
                ? 'border-red-300 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-pulse-500'
            }`}
          />
          {errors.phone && <p className="mt-1 text-sm text-red-600">{errors.phone}</p>}
        </div>
        
        <div className="flex-1">
          <label htmlFor="interest" className="block text-sm font-medium text-gray-700">I am interested in *</label>
          <Select 
            value={formData.interest} 
            onValueChange={(value) => {
              setFormData({ ...formData, interest: value });
              if (errors.interest) {
                setErrors(prev => ({ ...prev, interest: "" }));
              }
            }}
          >
            <SelectTrigger 
              id="interest"
              className={`mt-1 w-full rounded-xl ${
                errors.interest ? 'border-red-300' : 'border-gray-300'
              }`}
            >
              <SelectValue placeholder="Select option" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="free-testing">Free Testing Access Only</SelectItem>
              <SelectItem value="free-or-paid">Free Testing Access or Paid Full Access</SelectItem>
            </SelectContent>
          </Select>
          {errors.interest && <p className="mt-1 text-sm text-red-600">{errors.interest}</p>}
        </div>
        
        <div className="flex-1">
          <label htmlFor="message" className="block text-sm font-medium text-gray-700">
            One sentence on what you're most interested in testing *
          </label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            rows={4}
            required
            className={`mt-1 w-full rounded-xl border px-3 py-2 focus:outline-none focus:ring-2 ${
              errors.message 
                ? 'border-red-300 focus:ring-red-500' 
                : 'border-gray-300 focus:ring-pulse-500'
            }`}
          />
          {errors.message && <p className="mt-1 text-sm text-red-600">{errors.message}</p>}
        </div>
        
        <div>
          <button 
            type="submit" 
            disabled={submitting} 
            className="w-full px-6 py-3 bg-pulse-500 hover:bg-pulse-600 disabled:bg-gray-400 text-white font-medium rounded-full transition-colors duration-300"
          >
            {submitting ? "Submitting..." : "Submit Application"}
          </button>
        </div>
      </form>
    </>
  );
};

export default ApplyForm;