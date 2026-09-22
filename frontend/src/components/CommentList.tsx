interface CommentItem {
  id: number;
  authorName: string;
  content: string;
  createdAt: string;
}

interface CommentListProps {
  comments: CommentItem[];
}

function CommentList({ comments }: CommentListProps) {
  if (comments.length === 0) {
    return <p>Aucun commentaire pour le moment.</p>;
  }

  return (
    <section>
      <h2>Commentaires</h2>

      <ul>
        {comments.map((comment) => (
          <li key={comment.id}>
            <strong>{comment.authorName}</strong>
            <p>{comment.content}</p>
            <small>{comment.createdAt}</small>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default CommentList;