/**
 * tracing_tools.hpp
 *
 *  Created on: 04.08.2015
 *      Author: Ingo Luetkebohle <ingo.luetkebohle@de.bosch.com>
 *
 * HINT: For user-defined tracing, you mostly need "trace_message_processed".
 */

#ifndef CLIENTS_ROSCPP_INCLUDE_ROS_TRACING_TOOLS_H_
#define CLIENTS_ROSCPP_INCLUDE_ROS_TRACING_TOOLS_H_

#include <stdint.h>
#include <boost/shared_ptr.hpp>

//#include "ros/callback_queue_interface.h"

namespace ros {
	// forward declaration of a ros helper class
	class SubscriptionCallbackHelper;
	class CallbackInterface;
	typedef class boost::shared_ptr<ros::CallbackInterface> CallbackInterfacePtr;
	typedef boost::shared_ptr<SubscriptionCallbackHelper> SubscriptionCallbackHelperPtr;

	/**
	 * Wrapper interface for tracing.
	 *
	 * For application developers, look at TracingTools::trace_message_processed
	 * mainly. If you create your own threads (which, if you're using ROS, you
	 * can often avoid, btw), also look at TracingTools::trace_task_init.
	 *
	 * Middleware developers might need all of it, but I've done the integration
	 * with ROS Indigo already, and newer versions should be easy, too.
	 */
	class TracingTools {
	public:
		/// report lttng compile status
		static bool lttng_status() throw();
		/// emit a tracepoint specifying a name for this thread.
		/// also set's procname, and tries to create something that's
		/// unique within 16 chars by truncating task_name if necessary
		static void trace_task_init(const char* task_name, const char* owner=NULL);
		// emit a tracepoint giving the node name and its version
		/// also set's procname, but be aware that's limited to 16 chars
		static void trace_node_init(const char* node_name, unsigned int roscpp_version);

		static void trace_timer_added(const void* fun_ptr,
				const char* type_info, int period_sec, int period_nsec);

		/// get the function being pointed to by the CallbackInterfacePtr
		static const void* getCallbackFunction(const CallbackInterfacePtr& cb);
		/// try to get a name for the function inside the CallbackInterfacePtr
		static std::string getCallbackInfo(const CallbackInterfacePtr& cb);

		/**
		 * Emit tracing information linking the function ptr's name to the
		 * given reference pointer.
		 */
		static void trace_name_info(const void* fun_ptr, const void* ref);

		/**
		* Mark the processing of a given "message". Note that, by using
		* internal message-names, this also constitutes the main tracepoint
		* for *user-defined tracing.*
		*
		* Hint: Every trace message also includes the timestamp of the
		* trace function call with microsecond precision. If the time of
		* processing and of receipt is almost the same, this is often
		* sufficient. OTOH, if you process message at fixed rates, it can be
		* useful.
		*
		* Hint2: The callback_ref argument is also necessary for disambiguation
		* if the same message could be processed in multiple places. If
		* the message-name itself is unique, you can omit it without impacting
		* analysis.
		*
		* @param message_name Name of the "message"
		* @param callback_ref Function pointer of the callback you're in
		* @param receipt_time_sec Seconds part of the receive time
		* @param receipt_time_nsec Nanoseconds part of the receive time
		*/
		static void trace_message_processed(const char* message_name,
				const void* callback_ref, const uint32_t receipt_time_sec,
				const uint32_t receipt_time_nsec);

		/**
		 * Trace the start of a function call through a function pointer.
		 *
		 * Note: If you internally wrap the user function in another function,
		 * use trace_callback_wrapper to establish a correspondence between
		 * this call and the user function.
		 *
		 * Note: This is intended for use by the middleware, which invokes
		 * user-defined functions through function pointers.
		 *
		 * @param ptr_ref Function pointer reference.
		 * @param data Function argument, if any. May be NULL.
		 * @param trace_id A unique id for this call. Could be a sequence number.
		 *
		 * @see trace_callback_wrapper
		 * @see trace_call_end
		 */
		static void trace_call_start(const void* ptr_ref, const void* data,
				const uint64_t trace_id);
		/**
		 * Trace the end of a user-callback invocation.
		 *
		 * @see trace_call_start.
		 */
		static void trace_call_end(const void* ptr_ref, const void* data,
				const uint64_t trace_id);

		static void trace_queue_delay(const char* queue_name,
				const void* ptr_ref, const void* data,
				const uint32_t entry_time_sec, const uint32_t entry_time_nsec);


		/**
		 * Emit tracing information that the timer identified by
		 * 'timer_ref' has been scheduled for invocation on the callback-queue
		 * using the wrapper callback 'callback_ref'.
		 */
		static void trace_timer_scheduled(const void* callback_ref,
				const void* timer_ref);

		static void trace_time_sleep(const void* callback_ref, int sleep_sec, int sleep_nsec);

		/// Trace meta-data on creation of a new connection
		static void trace_new_connection(const char* local_hostport_arg,
											  const char* remote_hostport_arg,
											  const void* channel_ref_arg,
											  const char* channel_type_arg,
											  const char* name_arg,
											  const char* data_type_arg);
		/// Trace meta-data on creation of a publisher link (incoming topic connection)
		static void trace_publisher_link_handle_message(const void* channel_ref_arg,
														const void* buffer_ref_arg);
		/// Trace a message being queue for publishing
		static void trace_publisher_message_queued(const char* topic_arg,
												   const void* buffer_ref_arg);
		/// Trace metadata on a message being written to the socket
		static void trace_subscriber_link_message_write(const void* message_ref_arg,
														const void* channel_ref_arg);
		/// Trace metadata on an incoming message being dropped (queue full, etc.)
		static void trace_subscriber_link_message_dropped(const void* message_ref_arg);
		/// Trace metadata on a message having been received and queued
		static void trace_subscription_message_queued(const char* topic_arg,
													  const void* buffer_ref_arg,
													  const void* queue_ref_arg,
													  const void* callback_ref_arg,
													  const void* message_ref_arg,
													  int receipt_time_sec_arg,
													  int receipt_time_nsec_arg);
		/// Trace metadata on a new subscription callback
		static void trace_subscriber_callback_added(const void* queue_ref_arg,
													const void* callback_ref_arg,
													const char* type_info_arg,
													const char* data_type_arg,
													const char* source_name_arg,
													int queue_size_arg);
	};

	std::string get_backtrace(int index = -1);
	std::string get_symbol(void* funptr);


	/**
	 * Traces the function pointer, the name of the function it points
	 * to, and the helper that will be used to call it.
	 */
	void trace_callback_wrapper(void* func_ptr,
			const SubscriptionCallbackHelperPtr& helper);

	/** Emit a trace message for a link in a processing chain.
			 * @param element the containing link element (usually 'this')
			 * @param caller_name if available, a reference to the caller of this
			 * 	element
			 * @param in_data_ref a pointer to the incoming data element,
			 *   for association to the preceding link
			 * @param out_data_ref a pointer to the outgoing data element, for
			 *   association with the succeeding link
			 * @param trace_id an optional id for distinguishing different traces
			 *   where the data ref's are the same
			 * */
	void trace_link(const char* element_name,
			const void* caller_name,
			const void* in_data_ref,
			const void* out_data_ref,
			const uint64_t trace_id);
}


#endif /* CLIENTS_ROSCPP_INCLUDE_ROS_TRACING_TOOLS_H_ */
