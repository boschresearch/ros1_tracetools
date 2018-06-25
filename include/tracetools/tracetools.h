/**
 * tracing_tools.hpp
 *
 *  Created on: 04.08.2015
 *      Author: Ingo Luetkebohle <ingo.luetkebohle@de.bosch.com>
 *
 * HINT: For user-defined tracing, you mostly need
 * "ros::trace::message_processed".
 */

#ifndef __TRACETOOLS_TRACETOOLS_H_
#define __TRACETOOLS_TRACETOOLS_H_

#include <boost/shared_ptr.hpp>
#include <boost/function.hpp>
#include <stdint.h>
#include <string>
#include <typeinfo>

//#include "ros/callback_queue_interface.h"

namespace ros {
namespace trace {
  template<class P>
  const void* get_ptr(const boost::function<void (P)>& func_ptr) {
#if BOOST_VERSION <= 106500
    return reinterpret_cast<void*>(func_ptr.functor.func_ptr);
#else
    return reinterpret_cast<void*>(func_ptr.functor.members.func_ptr);
#endif
  }

/// report whether tracing is compiled in
bool compile_status() throw();

/// emit a tracepoint specifying a name for this thread.
/// also set's procname, and tries to create something that's
/// unique within 16 chars by truncating task_name if necessary
void task_init(const char *task_name, const char *owner = NULL);
// emit a tracepoint giving the node name and its version
/// also set's procname, but be aware that's limited to 16 chars
void node_init(const char *node_name, unsigned int roscpp_version);

void timer_added(const void *fun_ptr, const char *type_info, int period_sec,
                 int period_nsec);
/**
 * Emit tracing information linking the function ptr's name to the
 * given reference pointer.
 */
void fn_name_info(const void *fun_ptr, const void *ref);

/**
 * Legacy compatibility function for above which takes a wrapper
 * function directly.
 */
template <typename T>
void callback_wrapper(const void *func_ptr, const boost::shared_ptr<T> &helper) {
  fn_name_info(func_ptr, helper.get());
}

/*** Trace methods for callback queue processing */

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
void message_processed(const char *message_name, const void *callback_ref,
                       const uint32_t receipt_time_sec,
                       const uint32_t receipt_time_nsec);

/**
 * Trace the start of a function call through a function pointer.
 *
 * Note: This should only be used if the exact function pointer given
 * here has been registered using trace_name_info. For the ROS subscription
 * queue, which creates new callback objects on every message, use
 * trace_subscriber_callback_start instead
 *
 * Note: This is intended for use by the middleware, which invokes
 * user-defined functions through function pointers.
 *
 * @param ptr_ref Function pointer reference.
 * @param data Function argument, if any. May be NULL.
 * @param trace_id A unique id for this call. Could be a sequence number.
 *
 * @see ros::trace::callback_wrapper
 * @see trace_call_end
 */
void call_start(const void *ptr_ref, const void *data, const uint64_t trace_id);
/**
 * Trace the end of a user-callback invocation.
 *
 * @see trace_call_start.
 */
void call_end(const void *ptr_ref, const void *data, const uint64_t trace_id);
/** Trace queue delay experienced by the given function pointer */
void queue_delay(const char *queue_name, const void *ptr_ref, const void *data,
                 const uint32_t entry_time_sec, const uint32_t entry_time_nsec);

/******* Trace methods for subscription queue processing. ******/

/**
 * Trace the invocation of a previously queued subscriber call.
 *
 * Note: This is intended for use by the middleware, which invokes
 * user-defined functions through function pointers.
 *
 * @param topic The topic the callback relates to
 * @param queue_ref The wrapper object referenced in
 * trace_subscriber_callback_added
 * @param callback_ref The target function pointer
 * @param message_ref The message (should match the id in
 * trace_subscription_message_queued)
 * @param receipt_time_sec Second part of receiption_time
 * @param receipt_time_nsec Nanosecond part of receiption_time
 *
 * @see trace_subscriber_callback_added
 * @see trace_subscription_message_queued
 */
void subscriber_call_start(const std::string &topic, const void *queue_ref,
                           const void *callback_ref, const void *message_ref,
                           int receipt_time_sec, int receipt_time_nsec);

/**
 * Marks the end of the call, same arguments as above.
 * */
void subscriber_call_end(const std::string &topic, const void *queue_ref,
                         const void *callback_ref, const void *message_ref,
                         int receipt_time_sec, int receipt_time_nsec);

/***** Timer-related tracing *****/

/**
 * Emit tracing information that the timer identified by
 * 'timer_ref' has been scheduled for invocation on the callback-queue
 * using the wrapper callback 'callback_ref'.
 */
void timer_scheduled(const void *callback_ref, const void *timer_ref);
void time_sleep(const void *callback_ref, int sleep_sec, int sleep_nsec);

/****** Network-related tracing ******/

/// Trace metadata on creation of a new connection
void new_connection(const char *local_hostport_arg,
                    const char *remote_hostport_arg,
                    const void *channel_ref_arg, const char *channel_type_arg,
                    const char *name_arg, const char *data_type_arg);
/// Trace metadata on creation of a publisher link (incoming topic connection)
void publisher_link_handle_message(const void *channel_ref_arg,
                                   const void *buffer_ref_arg);
/// Trace metadata on a new subscription callback
void subscriber_callback_added(const void *queue_ref_arg,
                               const void *callback_ref_arg,
                               const char *type_info_arg,
                               const char *data_type_arg,
                               const char *source_name_arg, int queue_size_arg);

/// Trace a message being queue for publishing
void publisher_message_queued(const char *topic_arg,
                              const void *buffer_ref_arg);
void publisher_message_queued(const std::string &topic_arg,
                              const void *buffer_ref_arg);
/// Trace on a message being written to the socket
void subscriber_link_message_write(const void *message_ref_arg,
                                   const void *channel_ref_arg);
/// Trac on an incoming message being dropped (queue full, etc.)
void subscriber_link_message_dropped(const void *message_ref_arg);
/// Trace on a message having been received and queued
void subscription_message_queued(const char *topic_arg,
                                 const void *buffer_ref_arg,
                                 const void *queue_ref_arg,
                                 const void *callback_ref_arg,
                                 const void *message_ref_arg,
                                 int receipt_time_sec_arg,
                                 int receipt_time_nsec_arg);
void subscription_message_dropped(const char *topic_arg, const void *buffer_arg,
                                  const void *queue_ref_arg,
                                  const void *callback_ref_arg,
                                  const void *message_ref_arg,
                                  int receipt_time_sec, int receipt_time_nsec);

/** Emit a trace message for a link in a processing chain.
                 * @param element the containing link element (usually 'this')
                 * @param caller_name if available, a reference to the caller of
 * this
                 * 	element
                 * @param in_data_ref a pointer to the incoming data element,
                 *   for association to the preceding link
                 * @param out_data_ref a pointer to the outgoing data element,
 * for
                 *   association with the succeeding link
                 * @param trace_id an optional id for distinguishing different
 * traces
                 *   where the data refcallback_wrapper's are the same
                 * */
void link_step(const char *element_name, const void *caller_name,
               const void *in_data_ref, const void *out_data_ref,
               const uint64_t trace_id);

// some helpers, not for public consumption
namespace impl {
/// get the function being pointed to by the CallbackInterfacePtr
template <typename T>
const void *getCallbackFunction(const boost::shared_ptr<T> &cb) {
  return cb.get();
}

/// try to get a name for the function inside the CallbackInterfacePtr
std::string getCallbackInfo(const void *func_ptr, const char *name);

template <typename T>
std::string getCallbackInfo(const boost::shared_ptr<T> &cb) {
  return getCallbackInfo(cb.get(), typeid(*cb).name());
}
std::string get_backtrace(int index = -1);
std::string get_symbol(void *funptr);
}
}
}

#endif /* __TRACETOOLS_TRACETOOLS_H_ */
