import { motion } from "framer-motion";

export default function Card({ title, badge, right, children }) {
  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 10, scale: 0.99 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25 }}
    >
      <div className="card-head">
        <div className="card-title">
          <span>{title}</span>
          {badge ? <span className="badge">{badge}</span> : null}
        </div>
        {right ? right : null}
      </div>
      <div className="card-body">{children}</div>
    </motion.div>
  );
}
